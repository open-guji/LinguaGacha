import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { Item } from "../../../domain/item";
import { GuishuiPageFormat } from "./guishuipage-format";

let temp_dir = "";

beforeEach(() => {
  temp_dir = fs.mkdtempSync(path.join(os.tmpdir(), "linguagacha-guishuipage-format-"));
});

afterEach(() => {
  fs.rmSync(temp_dir, { recursive: true, force: true });
});

describe("GuishuiPageFormat", () => {
  it("按 pages 数组顺序生成条目，id 保存到 extra_field", async () => {
    const format = new GuishuiPageFormat();

    const items = await format.read_from_stream(
      new TextEncoder().encode(JSON.stringify({ id: "00154", pages: ["第一頁原文", "第二頁原文"] })),
      "00154.json",
    );

    expect(items.map((item) => [item.src, item.dst, item.row, item.extra_field])).toEqual([
      ["第一頁原文", "", 0, "00154"],
      ["第二頁原文", "", 1, "00154"],
    ]);
  });

  it("没有字符串 pages 数组时不按谷水书页解析", async () => {
    const format = new GuishuiPageFormat();

    await expect(
      format.read_from_stream(new TextEncoder().encode(JSON.stringify({ id: "00154" })), "a.json"),
    ).resolves.toEqual([]);
    await expect(
      format.read_from_stream(
        new TextEncoder().encode(JSON.stringify({ id: "00154", pages: [1, 2] })),
        "a.json",
      ),
    ).resolves.toEqual([]);
    await expect(
      format.read_from_stream(new TextEncoder().encode(JSON.stringify(["a", "b"])), "a.json"),
    ).resolves.toEqual([]);
  });

  it("写回时按 row 还原 pages 顺序并恢复 id", async () => {
    const format = new GuishuiPageFormat();
    await format.write_to_path(
      [
        Item.from_json({
          src: "第一頁原文",
          dst: "第一頁，原文。",
          row: 0,
          file_type: "GUISHUIPAGE",
          file_path: "00154.json",
          extra_field: "00154",
        }),
        Item.from_json({
          src: "第二頁原文",
          dst: "",
          row: 1,
          file_type: "GUISHUIPAGE",
          file_path: "00154.json",
          extra_field: "00154",
        }),
      ],
      {
        translated_path: temp_dir,
        bilingual_path: path.join(temp_dir, "bilingual"),
      },
    );

    expect(JSON.parse(fs.readFileSync(path.join(temp_dir, "00154.json"), "utf-8"))).toEqual({
      id: "00154",
      pages: ["第一頁，原文。", "第二頁原文"],
    });
  });
});
