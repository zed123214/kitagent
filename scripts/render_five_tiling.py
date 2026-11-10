"""Render the README five-slab animation. Requires Pillow >= 10.

python render_five_tiling.py --font /path/to/CJK-font.ttf --output ./assets
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1120, 680
BG, PANEL, INK, MUTED = '#0b1220', '#142137', '#eff6ff', '#9badc6'
CYAN, MINT, RED, LINE = '#59ccfa', '#67e2ba', '#ff907f', '#2b3c55'
FRAMES, FPS = 160, 8

def render(lang, frame, font_path):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    fonts = {n: ImageFont.truetype(font_path, n) for n in [16, 18, 20, 23, 28, 34, 42]}
    def t(x, y, s, size=20, color=INK):
        d.text((x,y), s, font=fonts[size], fill=color)
    def center(x,y,s,size=20,color=INK):
        t(x-d.textlength(s,font=fonts[size])/2,y,s,size,color)
    def box(x,y,w,h,color=PANEL,outline=None):
        d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=color,outline=outline,width=2)
    def arrow(x1,y1,x2,y2,color=MINT):
        d.line((x1,y1,x2,y2),fill=color,width=3)
        d.polygon([(x2,y2),(x2-9,y2-5),(x2-9,y2+5)],fill=color)
    def s(zh,en): return zh if lang=='zh' else en
    stage = min(frame//40,3)
    p = (frame%40)/39
    t(38,25,'KITAGENT  /  OPERATOR LAB',16,CYAN)
    t(38,57,s('五分片 Tiling：把整组工作分均衡','Five-slab tiling: balance the whole workload'),34)
    t(38,107,'SparseFlashAttentionGrad  ·  512 = 128 + 128 + 128 + 64 + 64',20,MUTED)
    names = [s('切分查询行','Split query rows'),s('找到归约尾部','Find the reduction tail'),s('重新分配任务','Reassign the work'),s('双顺序对照','Compare both orders')]
    for i,n in enumerate(names):
        x=38+i*272
        box(x,151,258,42,'#213a50' if i==stage else PANEL)
        t(x+13,160,f'0{i+1}  '+n,18,MINT if i==stage else MUTED)

    if stage<3:
        # Proportional query-row geometry, not execution-time bars.
        t(40,215,s('查询行分片','QUERY ROW PARTITION'),18,MUTED)
        x=40
        widths=[250,250,250,125,125]
        for i,(n,w) in enumerate(zip([128,128,128,64,64],widths)):
            active=stage>0 or p>(i+1)*.10
            box(x,250,w-6,55,'#21465c' if active else PANEL)
            if active:center(x+(w-6)/2,262,str(n),23,CYAN)
            x+=w
        xs=[40+i*210 for i in range(5)]
        for i,x in enumerate(xs):
            short=i>=3
            box(x,345,194,198,PANEL,RED if stage==1 and short else LINE)
            center(x+97,359,s(('短块核 ' if short else '长块核 ')+str(i+1),('Short ' if short else 'Long ')+str(i+1)),20)
            box(x+16,400,162,44,'#21465c')
            center(x+97,409,s('查询计算','Query compute'),18,CYAN)
            if stage>=1:
                if stage==1:
                    label=s('dK / dV 归约','dK / dV reduction') if short else s('归约任务','Reduction work')
                    box(x+16,459,162,58,'#583537' if short else '#1c3e3a')
                    center(x+97,475,label,16,RED if short else MINT)
                else:
                    label=s('dK 归约','dK reduction') if short else s('分担 dV 归约','Share dV reduction')
                    box(x+16,459,162,58,'#1c3e3a')
                    center(x+97,475,label,16,MINT)
        if stage==0:
            center(560,570,s('将一个 128 行块拆成两个 64 行块，让第五个矩阵核参与查询计算。','Split one 128-row block into two 64-row blocks; engage the fifth matrix core.'),20)
        elif stage==1:
            center(560,570,s('行数更少，也可能最后完成：短块核还承担了额外归约。','Fewer query rows can still finish last when reductions pile up.'),23,RED)
        else:
            # A moving work packet connects short and long core groups.
            q=min(1,max(0,(p-.05)/.65)); q=q*q*(3-2*q)
            px=930-570*q
            d.line((930,327,360,327),fill=LINE,width=2)
            d.polygon([(355,327),(365,321),(365,333)],fill=MINT)
            box(px-50,312,100,30,'#2b6b59')
            center(px,316,s('归约任务','Reduction'),16,MINT)
            center(560,570,s('短块核保留 dK，长块核轮换分担 dV；输出归属与完整归约一起考虑。','Keep dK on short slabs; rotate dV across long slabs and preserve output ownership.'),20,MINT)
    else:
        t(40,219,s('910B3 · 组合候选 vs 连续 C1 对照','910B3 · Combined candidate vs contiguous-C1 control'),23,CYAN)
        for i,(title,b,c,g) in enumerate([(s('正序','Forward order'),'280.17','258.99','7.56%'),(s('反序','Reverse order'),'275.31','259.71','5.67%')]):
            x=40+i*530
            box(x,265,510,235)
            t(x+24,285,title,23,MUTED)
            t(x+24,334,b,42)
            arrow(x+189,363,x+235,363)
            t(x+257,334,c,42,MINT)
            t(x+430,350,'μs',20,MUTED)
            t(x+24,423,s('耗时下降  ','Time reduced  ')+g,28,MINT)
        center(560,548,s('测量 → 找到尾部 → 调整任务归属 → 配对复测','Measure → locate the tail → revise ownership → retest'),23)
        center(560,586,s('让查询计算和梯度归约一起参与负载均衡。','Balance query computation and gradient reduction together.'),20,MUTED)
    d.line((38,628,1082,628),fill=LINE,width=1)
    t(38,643,s('分块 · 协作 · 测量 · 迭代','TILE · COORDINATE · MEASURE · ITERATE'),16,MUTED)
    t(830,643,'github.com/zed123214/kitagent',16,MUTED)
    d.rounded_rectangle((38,622,38+1044*(frame+1)/FRAMES,625),radius=1,fill=MINT)
    return im

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--font',default='C:/Windows/Fonts/msyh.ttc')
    ap.add_argument('--output',default='assets')
    args=ap.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    for lang in ['zh','en']:
        frames=[render(lang,f,args.font) for f in range(FRAMES)]
        # One palette prevents color flicker as the animation advances.
        swatches=Image.new('RGB',(W*4,H))
        for j,f in enumerate([25,65,105,145]):
            swatches.paste(frames[f],(j*W,0))
        palette=swatches.quantize(colors=128)
        indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
        stem='five-tiling-demo'+('.en' if lang=='en' else '')
        indexed[0].save(out/(stem+'.gif'),save_all=True,append_images=indexed[1:],duration=125,loop=0,optimize=True,disposal=1)
        frames[145].save(out/(stem+'.png'))
        contact=Image.new('RGB',(1120,680))
        for j,f in enumerate([25,65,105,145]):
            contact.paste(frames[f].resize((560,340)),((j%2)*560,(j//2)*340))
        contact.save(out/(stem+'-preview.png'))
        print(stem, (out/(stem+'.gif')).stat().st_size)

if __name__=='__main__': main()
