import { JsonTool } from "../../../shared/utils/json-tool";
import { decode_text_content } from "../../../shared/utils/text-tool";
import {
  effective_export_text,
  group_items,
  write_text_file,
  type ExportPaths,
} from "./file-format-shared";
import { Item, read_json_record } from "../../../domain/item";

/**
 * 谷水书页格式：{"id": string, "pages": string[]}，每个 pages 元素整体作为一条翻译条目
 */
export class GuishuiPageFormat {
  /**
   * 只接受携带字符串 pages 数组的对象，避免和其它 JSON 格式互相误判
   */
  public async read_from_stream(content: Uint8Array, rel_path: string): Promise<Item[]> {
    const record = read_json_record(await this.parse_json_with_encoding(content));
    const pages = record["pages"];
    if (!Array.isArray(pages) || !pages.every((page) => typeof page === "string")) {
      return [];
    }
    const id = typeof record["id"] === "string" ? record["id"] : "";
    return pages.map((src, index) =>
      Item.from_json({
        src,
        dst: "",
        row: index,
        file_type: "GUISHUIPAGE",
        file_path: rel_path,
        extra_field: id,
      }),
    );
  }

  /**
   * 写回时按 row 还原 pages 顺序，id 取自条目携带的原始值
   */
  public async write_to_path(items: Item[], paths: ExportPaths): Promise<void> {
    for (const [rel_path, group] of group_items(items, "GUISHUIPAGE")) {
      const sorted = [...group].sort((left, right) => left.row - right.row);
      const id = sorted.find((item) => typeof item.extra_field === "string" && item.extra_field !== "")
        ?.extra_field;
      const data = {
        id: typeof id === "string" ? id : "",
        pages: sorted.map((item) => effective_export_text(item)),
      };
      await write_text_file(
        `${paths.translated_path}/${rel_path}`,
        JsonTool.stringifyStrict(data, { indent: 4 }),
      );
    }
  }

  /**
   * JSON 先按 UTF-8 严格解析，失败时再走编码探测兼容旧资源文件
   */
  private async parse_json_with_encoding(content: Uint8Array): Promise<unknown> {
    try {
      return JsonTool.parseStrict(content);
    } catch {
      return JsonTool.parseStrict(await decode_text_content(content));
    }
  }
}
