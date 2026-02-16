import requests, re
from Crypto.Cipher import AES
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich import box
import time

console = Console()
models = [
    "DeepSeek-V1", "DeepSeek-V2", "DeepSeek-V2.5", "DeepSeek-V3", "DeepSeek-V3-0324",
    "DeepSeek-V3.1", "DeepSeek-V3.2", "DeepSeek-R1", "DeepSeek-R1-0528", "DeepSeek-R1-Distill",
    "DeepSeek-Prover-V1", "DeepSeek-Prover-V1.5", "DeepSeek-Prover-V2", "DeepSeek-VL",
    "DeepSeek-Coder", "DeepSeek-Coder-V2", "DeepSeek-Coder-6.7B-base", "DeepSeek-Coder-6.7B-instruct"
]
print(Panel.fit("🤖 [bold cyan]DEEPSEEK CHAT[/bold cyan]", border_style="cyan"))
print("\n[bold yellow]📋 اختر النموذج:[/bold yellow]\n")
table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
table.add_column("الرقم", style="cyan", justify="center")
table.add_column("النموذج", style="white")

for i, m in enumerate(models, 1):
    table.add_row(f"[bold]{i}[/bold]", m)

console.print(table)

# ===== اختيار النموذج =====
choice = Prompt.ask("\n[bold green]👉 الرقم[/bold green]")
model = models[int(choice)-1]
print(f"[bold green]✅ تم اختيار:[/bold green] [white on blue] {model} [/white on blue]\n")

# ===== حل التحدي =====
with console.status("[bold yellow]🔄 جاري تجهيز الجلسة..."):
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Android)'})
    
    r = s.get('https://asmodeus.free.nf/')
    nums = re.findall(r'toNumbers\("([a-f0-9]+)"\)', r.text)
    key, iv, data = [bytes.fromhex(n) for n in nums[:3]]
    
    s.cookies.set('__test', AES.new(key, AES.MODE_CBC, iv).decrypt(data).hex(), domain='asmodeus.free.nf')
    s.get('https://asmodeus.free.nf/index.php?i=1')    
    time.sleep(0.5)
print("[bold green]✅ الجلسة جاهزة![/bold green]")
print(Panel.fit("[bold]💬 اكتب رسالتك (أو 'خروج' للإنهاء)[/bold]", border_style="green"))
while True:
    msg = Prompt.ask("\n[bold cyan]📝 أنت[/bold cyan]").strip()
    
    if msg in ['خروج', 'exit', 'quit']:
        print("[bold red]👋 وداعاً![/bold red]")
        break
    
    if not msg:
        continue
    
    with console.status("[bold yellow]⏳ جاري التفكير..."):
        r = s.post('https://asmodeus.free.nf/deepseek.php', 
                   params={'i': '1'}, 
                   data={'model': model, 'question': msg})
        
        reply = re.search(r'<div class="response-content">(.*?)</div>', r.text, re.DOTALL)
        response_text = reply.group(1) if reply else 'تم الإرسال'
    
    print(f"\n[bold magenta]🤖 {model}:[/bold magenta]")
    print(Panel(response_text, border_style="magenta"))