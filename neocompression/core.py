import os
from pathlib import Path
from typing import Dict, List, Tuple

MAGIC = "NEOCMP1"


def file_to_binary(path: Path) -> str:
    data = path.read_bytes()
    return "".join(f"{byte:08b}" for byte in data)


def binary_to_bytes(bitstring: str) -> bytes:
    # Pad to full bytes
    if len(bitstring) % 8 != 0:
        bitstring = bitstring + "0" * (8 - (len(bitstring) % 8))
    return int(bitstring, 2).to_bytes(len(bitstring) // 8, "big")


def walk_path(root: Path) -> List[Path]:
    if root.is_file():
        return [root]
    return [p for p in root.rglob("*") if p.is_file()]


def build_compression_dict(binary_source: str, max_patterns: int = 94) -> Dict[str, str]:
    patterns: Dict[str, int] = {}
    min_len = 4
    max_len = min(32, max(len(binary_source) // 10, min_len))

    for length in range(max_len, min_len - 1, -1):
        step = max(1, length // 2)
        for i in range(0, len(binary_source) - length + 1, step):
            pattern = binary_source[i : i + length]
            patterns[pattern] = patterns.get(pattern, 0) + 1

    sorted_patterns = sorted(
        patterns.items(), key=lambda x: (x[1], len(x[0])), reverse=True
    )

    ascii_code = 33
    compression_dict: Dict[str, str] = {}

    for pattern, count in sorted_patterns[:max_patterns]:
        if count > 1 and ascii_code <= 126:
            compression_dict[pattern] = chr(ascii_code)
            ascii_code += 1

    return compression_dict


def analyze_chunk_structure(
    binary_chunk: str, min_segment_size: int = 4, max_segment_size: int = 32
):
    chunk_length = len(binary_chunk)
    analysis = {
        "total_bits": chunk_length,
        "optimal_segments": [],
        "leftover_bits": None,
        "segment_sizes": [],
        "recommended_padding": 0,
    }

    if chunk_length == 0:
        return analysis

    if chunk_length < 64:
        analysis["optimal_segments"] = [binary_chunk]
        analysis["segment_sizes"] = [chunk_length]
        return analysis

    pattern_scores: Dict[int, float] = {}

    for seg_size in range(max_segment_size, min_segment_size - 1, -1):
        segment_count = chunk_length // seg_size
        remainder = chunk_length % seg_size

        if segment_count == 0:
            continue

        pattern_frequency: Dict[str, int] = {}
        for i in range(0, segment_count * seg_size, seg_size):
            segment = binary_chunk[i : i + seg_size]
            pattern_frequency[segment] = pattern_frequency.get(segment, 0) + 1

        repeat_score = sum(count - 1 for count in pattern_frequency.values())
        pattern_scores[seg_size] = repeat_score / max(segment_count, 1)

    if pattern_scores:
        best_size = max(pattern_scores.keys(), key=lambda k: pattern_scores[k])
        segment_count = chunk_length // best_size

        for i in range(0, segment_count * best_size, best_size):
            seg = binary_chunk[i : i + best_size]
            analysis["optimal_segments"].append(seg)
            analysis["segment_sizes"].append(best_size)

        leftover_start = segment_count * best_size
        if leftover_start < chunk_length:
            analysis["leftover_bits"] = binary_chunk[leftover_start:]
            if len(analysis["leftover_bits"]) >= min_segment_size:
                analysis["optimal_segments"].append(analysis["leftover_bits"])
                analysis["segment_sizes"].append(len(analysis["leftover_bits"]))
            else:
                analysis["recommended_padding"] = (
                    min_segment_size - len(analysis["leftover_bits"])
                )
    else:
        segment_size = min(64, max(8, 2 ** (chunk_length.bit_length() - 1)))
        for i in range(0, chunk_length, segment_size):
            seg = binary_chunk[i : i + segment_size]
            if seg:
                analysis["optimal_segments"].append(seg)
                analysis["segment_sizes"].append(len(seg))

    return analysis


def compress_binary_chunk(
    binary_chunk: str, global_dict: Dict[str, str] | None = None
) -> Tuple[str, Dict[str, str], Dict]:
    if not binary_chunk:
        return "", {}, {"has_leftover": False, "padding_bits": 0, "total_bits": 0}

    analysis = analyze_chunk_structure(binary_chunk)

    pattern_dict = global_dict or build_compression_dict(binary_chunk)
    chunk_key = {v: k for k, v in pattern_dict.items()}

    compressed_parts: List[str] = []
    leftover_handling: Dict = {
        "has_leftover": analysis["leftover_bits"] is not None,
        "padding_bits": analysis["recommended_padding"],
        "total_bits": analysis["total_bits"],
    }

    for seg, seg_size in zip(
        analysis["optimal_segments"], analysis["segment_sizes"]
    ):
        if seg in pattern_dict:
            compressed_parts.append(pattern_dict[seg])
        elif seg_size >= 8:
            compressed_parts.append(f"\\s{seg_size}:{seg}")
        else:
            compressed_parts.append(f"\\t{seg}")

    if analysis["recommended_padding"] > 0:
        padding_bits = "0" * analysis["recommended_padding"]
        compressed_parts.append(f"\\p{padding_bits}")
        leftover_handling["padding_used"] = padding_bits

    return "".join(compressed_parts), chunk_key, leftover_handling


def decompress_binary_chunk(compressed_chunk: str, chunk_key: Dict[str, str]) -> str:
    binary_parts: List[str] = []
    i = 0

    while i < len(compressed_chunk):
        char = compressed_chunk[i]

        if char == "\\":
            if i + 1 >= len(compressed_chunk):
                break
            escape_type = compressed_chunk[i + 1]

            if escape_type == "s":
                size_end = compressed_chunk.find(":", i + 2)
                if size_end == -1:
                    i += 2
                    continue
                size = int(compressed_chunk[i + 2 : size_end])
                bits_start = size_end + 1
                bits_end = bits_start + size
                segment = compressed_chunk[bits_start:bits_end]
                binary_parts.append(segment)
                i = bits_end
            elif escape_type == "t":
                bits_start = i + 2
                bits_end = bits_start
                while bits_end < len(compressed_chunk) and compressed_chunk[bits_end] != "\\":
                    bits_end += 1
                segment = compressed_chunk[bits_start:bits_end]
                binary_parts.append(segment)
                i = bits_end
            elif escape_type == "p":
                bits_start = i + 2
                bits_end = bits_start
                while bits_end < len(compressed_chunk) and compressed_chunk[bits_end] in "01":
                    bits_end += 1
                i = bits_end
            else:
                i += 2
        elif char in chunk_key:
            binary_parts.append(chunk_key[char])
            i += 1
        else:
            i += 1

    return "".join(binary_parts)


def compress_binary_stream(binary_chunks: List[str]):
    if not binary_chunks:
        return "", {}, []

    all_data = "".join(binary_chunks)
    global_dict = build_compression_dict(all_data) if all_data else {}

    compressed_chunks: List[str] = []
    chunk_metadata: List[Dict] = []
    chunk_keys: Dict[str, Dict[str, str]] = {}

    for idx, chunk in enumerate(binary_chunks):
        compressed, chunk_key, leftover = compress_binary_chunk(chunk, global_dict)
        key_id = f"K{idx}"
        chunk_keys[key_id] = chunk_key

        metadata = {
            "chunk_id": idx,
            "key_id": key_id,
            "original_bits": len(chunk),
            "compressed_chars": len(compressed),
            "segment_count": len(analyze_chunk_structure(chunk)["optimal_segments"]),
            "has_leftover": leftover["has_leftover"],
            "padding_used": leftover.get("padding_used", ""),
        }
        chunk_metadata.append(metadata)

        header = f"\\c{idx}:{len(compressed)}:"
        compressed_chunks.append(header + compressed)

    compressed_stream = "".join(compressed_chunks)

    master_key = {
        "chunk_keys": chunk_keys,
        "global_patterns": global_dict,
        "total_chunks": len(binary_chunks),
    }

    return compressed_stream, master_key, chunk_metadata


def decompress_binary_stream(compressed_stream: str, master_key: Dict) -> List[str]:
    binary_chunks: List[str] = []
    chunk_keys = master_key["chunk_keys"]

    i = 0
    while i < len(compressed_stream):
        if compressed_stream[i : i + 2] != "\\c":
            raise ValueError(f"Invalid chunk header at position {i}")

        header_end = compressed_stream.find(":", i + 2)
        if header_end == -1:
            raise ValueError("Malformed chunk header")
        chunk_id = int(compressed_stream[i + 2 : header_end])

        length_start = header_end + 1
        length_end = compressed_stream.find(":", length_start)
        if length_end == -1:
            raise ValueError("Malformed chunk length")
        chunk_length = int(compressed_stream[length_start:length_end])

        data_start = length_end + 1
        data_end = data_start + chunk_length
        chunk_data = compressed_stream[data_start:data_end]

        key_id = f"K{chunk_id}"
        chunk_key = chunk_keys.get(key_id, {})
        binary_chunk = decompress_binary_chunk(chunk_data, chunk_key)
        binary_chunks.append(binary_chunk)

        i = data_end

    return binary_chunks


def compress_path(path: str | Path, out_file: str | Path, chunk_bits: int = 8192) -> None:
    root = Path(path)
    files = walk_path(root)

    all_binary_chunks: List[str] = []
    file_index: List[Dict] = []

    for f in files:
        rel = str(f.relative_to(root))
        bits = file_to_binary(f)
        # Split into chunks
        for i in range(0, len(bits), chunk_bits):
            chunk = bits[i : i + chunk_bits]
            all_binary_chunks.append(chunk)
            file_index.append({"path": rel, "offset_bits": i, "length_bits": len(chunk)})

    compressed_stream, master_key, metadata = compress_binary_stream(all_binary_chunks)

    # Container format: MAGIC\nJSON_META\n\nDATA
    import json

    container = {
        "index": file_index,
        "master_key": master_key,
        "metadata": metadata,
        "root_is_file": root.is_file(),
        "root_name": root.name,
    }

    header = MAGIC + "\n" + json.dumps(container, separators=(",", ":")) + "\n\n"
    Path(out_file).write_bytes(header.encode("utf-8") + compressed_stream.encode("ascii"))


def decompress_file(container_path: str | Path, out_dir: str | Path) -> None:
    import json

    data = Path(container_path).read_bytes()
    text = data.decode("utf-8", errors="ignore")

    if not text.startswith(MAGIC + "\n"):
        raise ValueError("Not a NeoCompression file")

    header_end = text.find("\n\n", len(MAGIC) + 1)
    if header_end == -1:
        raise ValueError("Corrupt container header")

    header_json = text[len(MAGIC) + 1 : header_end]
    container = json.loads(header_json)

    compressed_stream = text[header_end + 2 :]
    master_key = container["master_key"]
    index = container["index"]

    binary_chunks = decompress_binary_stream(compressed_stream, master_key)

    # Rebuild files
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    # Group chunks by file
    from collections import defaultdict

    file_bits: Dict[str, List[Tuple[int, str]]] = defaultdict(list)

    for meta, bits in zip(index, binary_chunks):
        file_bits[meta["path"]].append((meta["offset_bits"], bits))

    for rel_path, pieces in file_bits.items():
        pieces.sort(key=lambda x: x[0])
        bitstring = "".join(p for _, p in pieces)
        out_path = out_root / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(binary_to_bytes(bitstring))
