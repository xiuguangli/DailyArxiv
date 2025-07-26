"""
并发执行，使用 Gemini 批处理模式
- 支持分块（Chunking）提交
- 每次批处理动态获取/释放Key，并加入冷却机制
"""

from datetime import datetime
from logging import log
from dotenv import load_dotenv
import json
from tqdm import tqdm
from google import genai
import time
import os
import requests
from google.genai import types
import pathlib
import argparse
from box import Box
import threading
import queue
import uuid
import math

load_dotenv()
PROMPT1 = "用中文讲一下这篇文章的内容，并举一个例子说明问题和方法流程。"

PROMPT2 = """
请以文章作者的身份，深入剖析这篇文章，详细回顾您从选题到提出方法解决问题整个思维决策过程。最好是通过一个具体的例子进行说明。
请着重阐述：
0.您为什么选择这个研究内容。
1.您是如何一步步构思和界定研究问题的。
2.为了解决该问题，您在选择理论框架、研究方法和数据分析策略时，经历了怎样的思考、权衡和取舍。
3.在研究的每个关键阶段，您做出了哪些重要决策，并能解释这些决策背后的逻辑和依据。
"""

# 配置参数
CONFIG = Box({
    "ghostscript": {
        "quality": "screen",
        "compress_threshold_mb": 20,
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "api_key_lists": os.environ.get("GEMINI_API_KEYS", "").split(","),
        "max_concurrency": 2,
        "polling_interval_s": 30,
        "batch_size": 10,
        "key_cooldown_s": 20, # 【新增】每个Key使用后的冷却时间（秒）
    },
    "data": {
        "base_dir":"public/data",
    },
    "processing": {
        "save_interval": 10,
    },
    "update_info":{
         "gemini":{
            "field": "gemini2.5flash",
            "prompt": PROMPT1,
         },
         "overall":{
            "field": "overall_idea",
            "prompt": PROMPT2,
         }
    }
})

# ... (check_ghostscript, compress_pdf, download_file_with_progress 函数保持不变) ...
def check_ghostscript():
    import subprocess
    try:
        subprocess.run(['gs', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

GHOSTSCRIPT_AVAILABLE = check_ghostscript()
if GHOSTSCRIPT_AVAILABLE:
    print("Ghostscript已安装，PDF压缩功能可用")
else:
    print("未安装Ghostscript，将跳过压缩步骤")

def compress_pdf_with_ghostscript(input_path, output_path=None, quality="screen"):
    import subprocess, tempfile, shutil
    try:
        if output_path is None: output_path = input_path
        temp_file = None
        if output_path == input_path:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_output = temp_file.name
            temp_file.close()
        else: temp_output = output_path
        cmd = ['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', f'-dPDFSETTINGS=/{quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={temp_output}', input_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            if temp_file: shutil.move(temp_output, output_path)
            return True
        else:
            if temp_file and os.path.exists(temp_output): os.unlink(temp_output)
            return False
    except Exception: return False

def compress_pdf(input_path, output_path=None, quality="screen"):
    if not GHOSTSCRIPT_AVAILABLE or not os.path.exists(input_path): return False, 0, 0
    original_size = os.path.getsize(input_path)
    success = compress_pdf_with_ghostscript(input_path, output_path, quality)
    if success:
        compressed_size = os.path.getsize(output_path if output_path else input_path)
        return True, original_size, compressed_size
    else: return False, original_size, original_size

def download_file_with_progress(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for data in response.iter_content(chunk_size=8192): file.write(data)
        return True
    except Exception: return False


### --- 核心改造：每次批处理动态获取/释放Key并冷却 --- ###
def worker_batch(paper_slice, key_queue, lock, thread_idx, args, file_dir):
    field = CONFIG.update_info[args.update].field
    prompt = CONFIG.update_info[args.update].prompt
    model = CONFIG.gemini.model
    batch_size = CONFIG.gemini.batch_size
    
    progress_bar = tqdm(total=len(paper_slice), desc=f"线程{thread_idx+1}", position=thread_idx)
    
    total_chunks = math.ceil(len(paper_slice) / batch_size)

    # 遍历 paper_slice 的每个小块
    for i in range(0, len(paper_slice), batch_size):
        chunk = paper_slice[i : i + batch_size]
        chunk_num = (i // batch_size) + 1
        
        api_key = None # 初始化为None，确保finally块中可以安全检查
        try:
            # 【动态获取Key】: 为这个批次借用一个Key
            progress_bar.set_description(f"线程{thread_idx+1} [批次 {chunk_num}/{total_chunks}] 等待Key")
            api_key = key_queue.get()
            client = genai.Client(api_key=api_key)
            progress_bar.set_description(f"线程{thread_idx+1} [批次 {chunk_num}/{total_chunks}] 使用Key ...{api_key[-4:]}")

            # 为每个小块重置这些列表
            batch_requests = []
            request_key_to_paper = {}
            uploaded_files_for_cleanup = []

            for paper in chunk:
                # ... PDF准备和上传逻辑不变 ...
                if paper.get(field) or not paper.get("pdf_url"):
                    progress_bar.update(1)
                    continue
                
                local_pdf_file = f"{paper.get('order', 'temp')}_{thread_idx+1}_{uuid.uuid4().hex[:8]}.pdf"
                if not download_file_with_progress(paper["pdf_url"], local_pdf_file):
                    progress_bar.update(1)
                    continue
                
                if GHOSTSCRIPT_AVAILABLE and os.path.getsize(local_pdf_file) > CONFIG.ghostscript.compress_threshold_mb * 1024 * 1024:
                    compress_pdf(local_pdf_file, quality=CONFIG.ghostscript.quality)

                try:
                    pdf_config = types.UploadFileConfig(mime_type='application/pdf')
                    uploaded_pdf = client.files.upload(path=local_pdf_file, config=pdf_config)
                    uploaded_files_for_cleanup.append(uploaded_pdf)
                except Exception as e:
                    os.remove(local_pdf_file)
                    progress_bar.update(1)
                    continue
                
                request_key = f"paper_{paper.get('order', uuid.uuid4().hex)}"
                request_key_to_paper[request_key] = paper

                batch_request = {"key": request_key, "request": {"contents": [types.Part.from_uri(uri=uploaded_pdf.uri, mime_type='application/pdf').to_dict(), {'text': prompt}], "model": f"models/{model}"}}
                batch_requests.append(batch_request)
                os.remove(local_pdf_file)

            if not batch_requests:
                progress_bar.update(len(chunk) - len(batch_requests))
                continue

            # ... 批处理提交和轮询逻辑不变 ...
            progress_bar.set_description(f"线程{thread_idx+1} [批次 {chunk_num}/{total_chunks}] 提交中")
            jsonl_filename = f"batch_input_thread_{thread_idx+1}.jsonl"
            with open(jsonl_filename, "w") as f:
                for req in batch_requests: f.write(json.dumps(req) + "\n")
            
            jsonl_config = types.UploadFileConfig(mime_type='application/jsonl')
            input_file = client.files.upload(path=jsonl_filename, config=jsonl_config)
            uploaded_files_for_cleanup.append(input_file)
            os.remove(jsonl_filename)

            batch_job = client.batches.create(source_file_name=input_file.name)

            completed_states = {'SUCCEEDED', 'FAILED', 'CANCELLED'}
            while batch_job.state.name not in completed_states:
                progress_bar.set_description(f"线程{thread_idx+1} [批次 {chunk_num}/{total_chunks}] 轮询: {batch_job.state.name}")
                time.sleep(CONFIG.gemini.polling_interval_s)
                batch_job = client.batches.get(name=batch_job.name)

            if batch_job.state.name == 'SUCCEEDED' and batch_job.result_file_name:
                result_file = client.files.get_file(name=batch_job.result_file_name)
                result_lines = result_file.read().decode('utf-8').strip().split('\n')
                
                successful_updates = 0
                for line in result_lines:
                    result = json.loads(line)
                    paper = request_key_to_paper.get(result.get('key'))
                    if not paper: continue
                    if 'response' in result and 'candidates' in result['response']:
                        try:
                            paper[field] = result['response']['candidates'][0]['content']['parts'][0]['text']
                            successful_updates += 1
                        except (KeyError, IndexError): paper[field] = "Error: Parse failed."
                    else: paper[field] = f"Error: {result.get('error', 'Unknown error.')}"
                
                if successful_updates > 0:
                    with lock:
                        with open(file_dir, "w", encoding="utf-8") as f:
                            json.dump(file_data_global, f, ensure_ascii=False, indent=4)

            # 清理当前批次上传的文件
            for f in uploaded_files_for_cleanup:
                try: client.files.delete(name=f.name)
                except Exception: pass
            
            progress_bar.update(len(batch_requests))
        
        finally:
            # 【动态释放Key】: 确保Key在批次处理完成后被归还
            if api_key:
                progress_bar.set_description(f"线程{thread_idx+1} [批次 {chunk_num}/{total_chunks}] Key冷却中")
                # 【密钥冷却】
                time.sleep(CONFIG.gemini.key_cooldown_s)
                key_queue.put(api_key)

    progress_bar.close()


# ... (process_file 函数保持不变)
def process_file(file_dir, args, key_queue):
    global file_data_global

    papers = file_data_global
    if not papers: return []

    field = CONFIG.update_info[args.update].field
    unprocessed_papers = [paper for paper in papers if not paper.get(field)]
    if not unprocessed_papers:
        print(f"{os.path.basename(file_dir)} 所有论文均已处理。")
        return []
        
    print(f"{os.path.basename(file_dir)} 共有 {len(unprocessed_papers)}/{len(papers)} 篇论文未处理。")
    
    # 注意：这里的并发数是线程数，实际API并发由Key的数量控制
    n_threads = min(CONFIG.gemini.max_concurrency, len(unprocessed_papers))
    if n_threads == 0:
        print("待处理论文不足，无法启动线程。")
        return unprocessed_papers

    threads = []
    lock = threading.Lock()

    paper_slices = [[] for _ in range(n_threads)]
    for idx, paper in enumerate(unprocessed_papers):
        paper_slices[idx % n_threads].append(paper)
        
    for i in range(n_threads):
        if not paper_slices[i]: continue
        t = threading.Thread(target=worker_batch, args=(paper_slices[i], key_queue, lock, i, args, file_dir))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    with lock:
        with open(file_dir, "w", encoding="utf-8") as f:
            json.dump(file_data_global, f, ensure_ascii=False, indent=4)
    print(f"最终文件已保存 -> {file_dir}")
    
    final_unprocessed_papers = [paper.get("order") for paper in papers if not paper.get(field)]
    return final_unprocessed_papers


def main():
    parser = argparse.ArgumentParser(description="使用Gemini API【分块批处理模式】处理论文摘要")
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--task', type=str, default="conference", help='任务类型')
    parser.add_argument('--date', type=str, default=today_str, help='日期')
    parser.add_argument('--file', type=str, default="CVPR.2023", help='文件名')
    parser.add_argument('--update', type=str, default="gemini", help='字段名')
    parser.add_argument('--concurrency', type=int, help='覆盖并发线程数')
    parser.add_argument('--polling_interval', type=int, help='覆盖批处理轮询间隔')
    parser.add_argument('--batch_size', type=int, help='覆盖批处理大小')
    parser.add_argument('--cooldown', type=int, help='覆盖Key冷却时间(秒)') # 【新增】
    
    args = parser.parse_args()

    if args.concurrency: CONFIG.gemini.max_concurrency = args.concurrency
    if args.polling_interval: CONFIG.gemini.polling_interval_s = args.polling_interval
    if args.batch_size: CONFIG.gemini.batch_size = args.batch_size
    if args.cooldown: CONFIG.gemini.key_cooldown_s = args.cooldown # 【新增】

    print(f"当前配置: 最大并发线程数={CONFIG.gemini.max_concurrency}, 批处理大小={CONFIG.gemini.batch_size}, 轮询间隔={CONFIG.gemini.polling_interval_s}s, Key冷却={CONFIG.gemini.key_cooldown_s}s")

    # ... (文件列表和Key队列逻辑不变) ...
    if args.task == "conference":
        file_list = [os.path.join(CONFIG.data.base_dir, f"{args.file}.json")]
    elif args.task == "arxiv":
        date = args.date
        year = date[:4]
        month = date[5:7]
        categories = ["cs.CV", "cs.AI", "cs.LG"]
        file_list = [os.path.join(CONFIG.data.base_dir, year, month, f"{date}_{category}.json") for category in categories]
    else: file_list = []

    api_key_list = [key for key in CONFIG.gemini.api_key_lists if key]
    if not api_key_list:
        print("错误：未找到任何有效的GEMINI_API_KEYS。")
        return
        
    key_queue = queue.Queue()
    for k in api_key_list:
        key_queue.put(k)

    max_file_retries = 3
    for file_dir in file_list:
        if not os.path.exists(file_dir):
            print(f"警告：文件 {file_dir} 不存在，跳过。")
            continue
            
        for i in range(max_file_retries):
            global file_data_global
            with open(file_dir, "r", encoding="utf-8") as f:
                file_data_global = json.load(f)
            
            res = process_file(file_dir, args, key_queue)
            if not res:
                print(f"文件 {file_dir} 全部处理完成。")
                break
            
            print(f"文件 {file_dir} 第{i+1}/{max_file_retries}轮处理后，仍有 {len(res)} 篇未成功。")
            if i < max_file_retries - 1:
                print("15秒后进行下一轮处理...")
                time.sleep(15)
        else:
            print(f"警告：文件 {file_dir} 经过 {max_file_retries} 轮处理后，仍有未完成的论文。")

if __name__ == "__main__":
    main()