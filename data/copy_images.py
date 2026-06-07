import os
import shutil

def copy_generated_images():
    # Source paths (AppData artifacts folder)
    src_dir = r"C:\Users\Chiteish\.gemini\antigravity\brain\335ed95f-7248-4a23-aa5f-218355c05018"
    src_img1 = os.path.join(src_dir, "web_visualizer_dashboard_1780855437447.png")
    src_img2 = os.path.join(src_dir, "react_leaflet_dashboard_1780855457693.png")

    # Destination paths (Project workspace)
    dest_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
    os.makedirs(dest_dir, exist_ok=True)
    dest_img1 = os.path.join(dest_dir, "web_visualizer_dashboard.png")
    dest_img2 = os.path.join(dest_dir, "react_leaflet_dashboard.png")

    # Copy files
    copied = 0
    if os.path.exists(src_img1):
        shutil.copy2(src_img1, dest_img1)
        print(f"Copied visualizer dashboard to: images/web_visualizer_dashboard.png")
        copied += 1
    else:
        print("Warning: Source image 1 not found.")

    if os.path.exists(src_img2):
        shutil.copy2(src_img2, dest_img2)
        print(f"Copied React + Leaflet map dashboard to: images/react_leaflet_dashboard.png")
        copied += 1
    else:
        print("Warning: Source image 2 not found.")

    if copied == 2:
        print("SUCCESS: Both images successfully copied to the project images/ directory!")
    else:
        print("Partial success or missing files.")

if __name__ == '__main__':
    copy_generated_images()
