import os
import shutil
import subprocess

OBSIDIAN_PROJECTS_PATH = "/home/jobran/Downloads/Projects"
GITHUB_REPO_LOCAL_PATH = "/home/jobran/Projects/github-portfolio-repo"
CONTENT_DEST_PATH = os.path.join(GITHUB_REPO_LOCAL_PATH, "content")

def should_publish(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(10)]
            frontmatter_started = False
            for line in lines:
                stripped = line.strip()
                if stripped == "---":
                    if not frontmatter_started:
                        frontmatter_started = True
                        continue
                    else:
                        break
                if frontmatter_started and "publish_to_portfolio" in stripped and "true" in stripped.lower():
                    return True
    except Exception as e:
        print(f"⚠️ خطأ أثناء قراءة الملف {file_path}: {e}")
    return False

def sync_portfolio():
    print("🔄 جاري فحص مجلد Obsidian للمشاريع الجديدة محلياً...")
    
    if not os.path.exists(CONTENT_DEST_PATH):
        os.makedirs(CONTENT_DEST_PATH, exist_ok=True)

    published_count = 0
    for root, _, files in os.walk(OBSIDIAN_PROJECTS_PATH):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                if should_publish(file_path):
                    dest_path = os.path.join(CONTENT_DEST_PATH, file)
                    shutil.copy(file_path, dest_path)
                    published_count += 1

    print(f"📦 تم العثور على {published_count} ملف مطابق لشروط النشر.")
    
    try:
        subprocess.run(["git", "-C", GITHUB_REPO_LOCAL_PATH, "add", "."], check=True)
        
        # فحص ما إذا كانت هناك تغييرات فعلية تستدعي الـ commit والـ push
        status_res = subprocess.run(["git", "-C", GITHUB_REPO_LOCAL_PATH, "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if status_res.stdout.strip():
            subprocess.run(["git", "-C", GITHUB_REPO_LOCAL_PATH, "commit", "-m", "Automated Portfolio Sync via Pure Python Script"], check=True)
            subprocess.run(["git", "-C", GITHUB_REPO_LOCAL_PATH, "push", "-u", "origin", "master"], check=True)
            print("🚀 تمت المزامنة والرفع إلى GitHub بنجاح!")
        else:
            print("📭 المستودع محدث بالكامل، لا توجد تغييرات جديدة لرفعها.")
            
    except subprocess.CalledProcessError as sub_err:
        print(f"❌ فشل عملية Git: {sub_err}")

if __name__ == "__main__":
    sync_portfolio()
