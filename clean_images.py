from PIL import Image, ImageSequence
import os

def make_gif_transparent_and_square(input_path):
    img = Image.open(input_path)
    
    # Kırpma ölçülerini belirle (Kare yapmak için)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    
    frames = []
    for frame in ImageSequence.Iterator(img):
        # Kareye kırp ve RGBA'ya çevir
        curr_frame = frame.crop((left, top, right, bottom)).convert("RGBA")
        datas = curr_frame.getdata()
        
        new_data = []
        for item in datas:
            # Siyah temizleme eşiğini biraz artırdık (40,40,40 altı şeffaf)
            # Ayrıca toplam parlaklığa da bakıyoruz ki silik gri kalmasın
            r, g, b, a = item
            if r < 45 and g < 45 and b < 45:
                # Siyaha yakın her şeyi tam şeffaf yap
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append(item)
        
        curr_frame.putdata(new_data)
        frames.append(curr_frame)
    
    if frames:
        frames[0].save(
            input_path, 
            save_all=True, 
            append_images=frames[1:], 
            loop=0, 
            duration=img.info.get('duration', 100),
            disposal=2
        )
        print(f"GIF optimize edildi ve kareye kırpıldı: {input_path}")

def remove_background(path):
    if path.endswith(".gif"):
        make_gif_transparent_and_square(path)
    else:
        # Green Screen removal for PNG
        img = Image.open(path).convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            r, g, b, a = item
            if g > 150 and g > r * 1.2 and g > b * 1.2:
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        img.save(path, "PNG")
        print(f"PNG temizlendi (Green Screen): {path}")

if __name__ == "__main__":
    assets_dir = "assets"
    # Sadece GIF'leri işle (Robot animasyonları)
    files = ["happy.gif", "angry.gif", "sleep.gif"]
    for filename in files:
        path = filename if os.path.exists(filename) else os.path.join(assets_dir, filename)
        if os.path.exists(path):
            remove_background(path)
