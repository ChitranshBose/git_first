import numpy as np
from collections import defaultdict, Counter
from PIL import Image
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976

def rgb2lab(rgb):
    return convert_color(sRGBColor(*[x/255.0 for x in rgb]), LabColor)

def find_nearest_general_color(color):
    color_lab = rgb2lab(color)
    min_dist = float('inf')
    nearest_color = None
    for general_color, shades in color_palette.items():
        for shade in shades:
            shade_lab = rgb2lab(shade)
            dist = delta_e_cie1976(color_lab, shade_lab)
            if dist < min_dist:
                min_dist = dist
                nearest_color = general_color
    return nearest_color

def get_color_name(color):
    return 'rgb({},{},{})'.format(*color)

def fetch_top_colors(req):
    global img_file, img_instance
    if req.method == "POST":
        form = UploadImage(req.POST, req.FILES)
        if form.is_valid():
            if 'img' in req.FILES:
                save = form.save()
                img_instance = form.instance
                img_file = os.path.join(settings.MEDIA_ROOT, str(save.img))
            image = img_instance
            k = int(req.POST['drop_down'])
            img_path = img_file

            with Image.open(img_path) as img_obj:
                img_colors = list(img_obj.getdata())
                if img_obj.mode == 'L':
                    return render(req, 'color_info.html', {'form': form, 'msg': "The image is Grayscale."})

                color_counts = defaultdict(int)
                for clr in img_colors:
                    general_color = find_nearest_general_color(clr[:3])
                    color_counts[general_color] += 1

                total_pixels = sum(color_counts.values())
                color_percentages = {clr: (count / total_pixels) * 100 for clr, count in color_counts.items()}
                color_percentages = dict(sorted(color_percentages.items(), key=lambda item: item[1], reverse=True)[:k])
                
                context = {
                    'form': form,
                    'image': image,
                    'top_colors': color_percentages
                }
                return render(req, 'color_info.html', context)
    else:
        form = UploadImage()
    images = Upload.objects.all()
    return render(req, 'color_info.html', {"images": images, 'form': form})
