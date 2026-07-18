#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[3]
sys.path.insert(0, str(SCRIPT_DIR))

import analyze_header_geometry
import analyze_visual_style
import validate_carousel


def font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("/System/Library/Fonts/Supplemental/PTMono.ttc")
    return ImageFont.truetype(str(path), 25) if path.exists() else ImageFont.load_default()


def synthetic_header(left_x: int = 88, right_x: int = 992, y: int = 60, left_color: str = "#D96C50") -> Image.Image:
    image = Image.new("RGB", (1080, 1350), "#F7F4EE")
    draw = ImageDraw.Draw(image)
    for x in range(0, 1081, 36):
        draw.line((x, 0, x, 210), fill="#E1DCD4")
    for row in range(0, 211, 36):
        draw.line((0, row, 1080, row), fill="#E1DCD4")
    face = font()
    draw.text((left_x, y), "[ gconf ]", fill=left_color, font=face, anchor="lm")
    draw.text((right_x, y), "01 / 06", fill="#77716C", font=face, anchor="rm")
    draw.text((88, 220), "Vibe Coding", fill="#171513", font=ImageFont.truetype(str(Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")), 72) if Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf").exists() else face)
    return image


def synthetic_style_slide(bottom_y: int = 1200, blue: bool = False) -> Image.Image:
    image = Image.new("RGB", (1080, 1350), "#F7F4EE")
    draw = ImageDraw.Draw(image)
    face = ImageFont.truetype(str(Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")), 64) if Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf").exists() else font()
    draw.text((88, 220), "Vibe Coding", fill="#171513", font=face)
    for y in (430, 650, 870, bottom_y):
        draw.text((88, y), "meaningful content row", fill="#171513", font=font())
    draw.rectangle((88, 180, 260, 195), fill="#D96C50")
    if blue:
        draw.rectangle((800, 400, 900, 500), fill="#2448FF")
    return image


class CarouselToolsTests(unittest.TestCase):
    def test_prepare_requires_confirmed_copy_decision(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "-B", str(SCRIPT_DIR / "prepare_design_context.py"),
                "--announcement-run", "research/announcement_drafts/runs/20260718T100953Z",
                "--decision-id", "missing-decision",
                "--permission-decision-id", "missing-permission-decision",
                "--carousel-file", "instagram-carousel-v6.md",
                "--references-dir", "Instagram/Прошлый Анонс",
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("copy approval gate failed", result.stdout)

    def test_header_geometry_accepts_matching_master(self) -> None:
        master = synthetic_header()
        result = analyze_header_geometry.compare(master, master.copy())
        self.assertTrue(result["ok"], result)

    def test_header_geometry_rejects_anchor_drift(self) -> None:
        master = synthetic_header()
        drifted = synthetic_header(left_x=115, right_x=955, y=80)
        result = analyze_header_geometry.compare(master, drifted)
        self.assertFalse(result["ok"])
        self.assertTrue(any("drift" in error for error in result["errors"]))

    def test_header_geometry_rejects_lost_coral_accent(self) -> None:
        master = synthetic_header()
        black_header = synthetic_header(left_color="#171513")
        result = analyze_header_geometry.compare(master, black_header)
        self.assertFalse(result["ok"])
        self.assertTrue(any("muted-coral" in error for error in result["errors"]))

    def test_normalize_varied_sources_to_1080_by_1350(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            sources = []
            for index, size in enumerate(((1024, 1536), (1536, 1024), (720, 1280), (1080, 1350), (800, 800), (1440, 2560)), 1):
                source = temp_path / f"source-{index}.png"
                Image.new("RGB", size, "orange").save(source)
                sources.append(source)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "normalize_carousel.py"), *map(str, sources), "--out-dir", str(temp_path / "out")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for index in range(1, 7):
                with Image.open(temp_path / f"out/slide-{index:02d}.png") as image:
                    self.assertEqual(image.size, (1080, 1350))

    def test_normalizer_has_no_format_switch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            source = temp_path / "source.png"
            Image.new("RGB", (1024, 1536), "orange").save(source)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "normalize_carousel.py"), str(source), "--out-dir", str(temp_path / "out"), "--format", "9:16"],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_normalizer_preserves_all_four_generated_edges(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            source = temp_path / "source.png"
            image = Image.new("RGB", (1092, 1440), "white")
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 30, 30), fill="red")
            draw.rectangle((1061, 1409, 1091, 1439), fill="blue")
            image.save(source)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "normalize_carousel.py"), str(source), "--out-dir", str(temp_path / "out")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(temp_path / "out/slide-01.png") as normalized:
                self.assertGreater(normalized.getpixel((0, 0))[0], 200)
                self.assertGreater(normalized.getpixel((1079, 1349))[2], 200)

    def test_structure_derivatives_are_grayscale_and_sources_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            refs = temp_path / "refs"
            refs.mkdir()
            feed = refs / "инстаграмм аккаунт gconf.PNG"
            Image.new("RGB", (300, 400), "blue").save(feed)
            slides = []
            for index in range(1, 7):
                path = refs / f"IMG_{index}.jpg"
                Image.new("RGB", (300, 400), (20 * index, 40, 220)).save(path)
                slides.append(path)
            before = {path: path.read_bytes() for path in [feed, *slides]}
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "prepare_structure_references.py"), "--references-dir", str(refs), "--out-dir", str(temp_path / "out")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for path, content in before.items():
                self.assertEqual(path.read_bytes(), content)
            with Image.open(temp_path / "out/slide-01.png") as derived:
                red, green, blue = derived.convert("RGB").getpixel((10, 10))
                self.assertEqual(red, green)
                self.assertEqual(green, blue)

    def test_visual_style_rejects_electric_blue(self) -> None:
        result = analyze_visual_style.analyze(synthetic_style_slide(blue=True), 1)
        self.assertFalse(result["ok"])
        self.assertTrue(any("electric-blue" in error for error in result["errors"]))

    def test_visual_style_rejects_underfilled_slide(self) -> None:
        result = analyze_visual_style.analyze(synthetic_style_slide(bottom_y=850), 1)
        self.assertFalse(result["ok"])
        self.assertTrue(any("content ends" in error or "vertical fill" in error for error in result["errors"]))

    def test_active_contract_has_no_story_format(self) -> None:
        files = [
            ROOT / ".agents/skills/gconf-instagram-carousel-designer/SKILL.md",
            ROOT / ".agents/skills/gconf-instagram-carousel-designer/references/design-system.md",
            ROOT / ".agents/skills/gconf-instagram-carousel-designer/references/output-contract.md",
            SCRIPT_DIR / "prepare_design_context.py",
            SCRIPT_DIR / "normalize_carousel.py",
            SCRIPT_DIR / "validate_carousel.py",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("9:16", text, path)
            self.assertNotIn("1080×1920", text, path)

    def test_v6_validator_rejects_legacy_overlay_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / "manifest.json").write_text('{"workflow_mode":"master-frame-generation","header_overlay_applied":true,"shared_header":{}}')
            errors = validate_carousel.validate(run)
            self.assertTrue(any("header_overlay_applied" in error for error in errors))
            self.assertTrue(any("legacy shared_header" in error for error in errors))

    def test_empty_run_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(validate_carousel.validate(Path(temp)))


if __name__ == "__main__":
    unittest.main()
