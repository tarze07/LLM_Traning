import os

files = [
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\02-clip-contrastive-pretraining\outputs\skill-clip-zero-shot_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\03-blip2-qformer-bridge\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\03-blip2-qformer-bridge\outputs\skill-modality-bridge-picker_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\04-flamingo-gated-cross-attention\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\04-flamingo-gated-cross-attention\outputs\skill-gated-bridge-diagnostic_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\05-llava-visual-instruction-tuning\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\05-llava-visual-instruction-tuning\outputs\skill-llava-vibes-eval_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\06-any-resolution-patch-n-pack\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\06-any-resolution-patch-n-pack\outputs\skill-resolution-budget-planner_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\07-open-weight-vlm-recipes\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\07-open-weight-vlm-recipes\outputs\skill-vlm-recipe-picker_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\08-llava-onevision-single-multi-video\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\08-llava-onevision-single-multi-video\outputs\skill-onevision-budget-planner_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\09-qwen-vl-family-dynamic-fps\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\09-qwen-vl-family-dynamic-fps\outputs\skill-qwen-vl-pipeline-designer_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\10-internvl3-native-multimodal\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\10-internvl3-native-multimodal\outputs\skill-native-vs-posthoc-auditor_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\11-chameleon-early-fusion-tokens\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\11-chameleon-early-fusion-tokens\outputs\skill-tokenizer-vs-adapter-picker_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\12-emu3-next-token-for-generation\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\12-emu3-next-token-for-generation\outputs\skill-token-gen-cost-analyzer_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\13-transfusion-autoregressive-diffusion\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\13-transfusion-autoregressive-diffusion\outputs\skill-two-loss-trainer-designer_pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\14-show-o-discrete-diffusion-unified\docs\pl.md",
    r"C:\poligon\LLM_Traning\phases\12-multimodal-ai\14-show-o-discrete-diffusion-unified\outputs\skill-unified-gen-model-picker_pl.md"
]

for idx, f in enumerate(files):
    if os.path.exists(f):
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        print(f"[{idx}] {os.path.basename(f)} - {len(content)} chars, {len(content.splitlines())} lines")
    else:
        print(f"[{idx}] MISSING: {f}")
