"""Exporta os arquivos de fabricacao (PDFs 1:1 para transferencia termica, Gerbers, furacao)."""
import os, subprocess, zipfile, glob, shutil
import pcbnew

MM = pcbnew.FromMM


def plot_pdf(pcb_path, outdir, name, layers, mirror=False, negative=False, drill_marks=True, title=''):
    board = pcbnew.LoadBoard(pcb_path)
    pc = pcbnew.PLOT_CONTROLLER(board)
    po = pc.GetPlotOptions()
    po.SetOutputDirectory(outdir)
    po.SetPlotFrameRef(False)
    po.SetAutoScale(False)
    po.SetScale(1.0)
    po.SetMirror(mirror)
    po.SetNegative(negative)
    po.SetBlackAndWhite(True)
    po.SetUseAuxOrigin(False)
    po.SetDrillMarksType(pcbnew.DRILL_MARKS_SMALL_DRILL_SHAPE if drill_marks else pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)
    po.SetPlotValue(False)
    po.SetPlotReference(True)
    po.SetSketchPadsOnFabLayers(False)
    po.SetPlotViaOnMaskLayer(False)
    po.SetPlotInvisibleText(False)
    po.SetSubtractMaskFromSilk(False)
    pc.OpenPlotfile(name, pcbnew.PLOT_FORMAT_PDF, title)
    for ly in layers:
        pc.SetLayer(ly)
        pc.PlotLayer()
    pc.ClosePlot()
    return os.path.join(outdir, os.path.basename(os.path.splitext(pcb_path)[0]) + '-' + name + '.pdf')


def export_all(pcb_path, outdir, base):
    os.makedirs(outdir, exist_ok=True)
    F, B, E, CM = pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.Edge_Cuts, pcbnew.Cmts_User
    files = []
    files.append(plot_pdf(pcb_path, outdir, '1-cobre-inferior-transferencia', [B, E, CM], mirror=False,
                          title='Cobre inferior - imprimir 100%'))
    files.append(plot_pdf(pcb_path, outdir, '2-cobre-superior-transferencia-espelhado', [F, E, CM], mirror=True,
                          title='Cobre superior (espelhado) - imprimir 100%'))
    files.append(plot_pdf(pcb_path, outdir, '3-mascara-montagem-componentes', [pcbnew.F_SilkS, E, CM], mirror=False,
                          drill_marks=False, title='Guia de montagem'))
    files.append(plot_pdf(pcb_path, outdir, '4-serigrafia-transferencia-espelhada', [pcbnew.F_SilkS, E, CM],
                          mirror=True, drill_marks=False, title='Serigrafia (espelhada) opcional'))
    files.append(plot_pdf(pcb_path, outdir, '5-fotolito-negativo-inferior', [B, E], mirror=False, negative=True,
                          title='Fotolito negativo (dry film) - inferior'))
    files.append(plot_pdf(pcb_path, outdir, '6-fotolito-negativo-superior-espelhado', [F, E], mirror=True,
                          negative=True, title='Fotolito negativo (dry film) - superior'))
    # Gerbers + furacao (para quem preferir mandar fabricar)
    gdir = os.path.join(outdir, 'gerber')
    os.makedirs(gdir, exist_ok=True)
    subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '--layers',
                    'F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts', '--subtract-soldermask',
                    '-o', gdir + '/', pcb_path], check=True, capture_output=True)
    subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th',
                    '--generate-map', '--map-format', 'pdf', '-o', gdir + '/', pcb_path], check=True,
                   capture_output=True)
    zp = os.path.join(outdir, f'{base}-gerber.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(gdir + '/*')):
            z.write(f, os.path.basename(f))
    for f in glob.glob(gdir + '/*-drl_map.pdf') + glob.glob(gdir + '/*-PTH-drl_map.pdf'):
        shutil.copy(f, os.path.join(outdir, '7-mapa-de-furacao.pdf'))
        break
    shutil.rmtree(gdir)
    # renomeia PDFs com nome curto
    out = []
    for f in files:
        nf = os.path.join(outdir, os.path.basename(f).replace(base + '-', ''))
        if os.path.exists(f):
            os.replace(f, nf)
            out.append(nf)
    return out + [zp]
