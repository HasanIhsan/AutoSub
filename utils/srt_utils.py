import re
from datetime import datetime

_TIME_RE = re.compile(r'^\\d{2}:\\d{2}:\\d{2},\\d{3}$')


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def srt_time_to_seconds(srt_time: str) -> float:
    if not _TIME_RE.match(srt_time):
        raise ValueError(f"Invalid SRT time: '{srt_time}'")
    h, m, rest = srt_time.split(":", 2)
    s, ms = rest.split(",", 1)
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0


def read_srt(file_path: str):
    subs = []
    with open(file_path, encoding="utf-8") as f:
        content = f.read().strip()
    for block in content.split("\n\n"):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        idx = lines[0].strip()
        times = lines[1]
        start, end = [t.strip() for t in times.split("-->")]
        text = " ".join(lines[2:]).strip()
        subs.append({"index": idx, "start": start, "end": end, "text": text})
    return subs


def smooth_srt(subs, min_gap=0.1, min_duration=0.5):
    
    smoothed, prev, prev_start, prev_end = [], None, None, None
    for curr in subs:
        try:
            cs = srt_time_to_seconds(curr['start'])
            ce = srt_time_to_seconds(curr['end'])
        except:
            continue
        if prev is None:
            prev, prev_start, prev_end = curr.copy(), cs, ce
            continue
        gap = cs - prev_end
        if gap < min_gap:
            prev['end'], prev['text'], prev_end = curr['end'], prev['text'] + ' ' + curr['text'], ce
        else:
            dur = prev_end - prev_start
            if dur < min_duration:
                prev['end'] = format_timestamp(prev_start + min_duration)
            smoothed.append(prev)
            prev, prev_start, prev_end = curr.copy(), cs, ce
    if prev:
        dur = prev_end - prev_start
        if dur < min_duration:
            prev['end'] = format_timestamp(prev_start + min_duration)
        smoothed.append(prev)
    return smoothed


def write_srt_n_words(aligned_result, audio_path, output_srt, words_per_subtitle):
    from whisperx.utils import format_timestamp as _fmt_ts
    all_w = [w for seg in aligned_result['segments'] for w in seg['words']]
    import os
    os.makedirs(os.path.dirname(output_srt) or ".", exist_ok=True)
    with open(output_srt, 'w', encoding='utf-8') as f:
        idx = 1
        for i in range(0, len(all_w), words_per_subtitle):
            chunk = all_w[i:i+words_per_subtitle]
            start, end = chunk[0]['start'], chunk[-1]['end']
            text = ' '.join(w['word'] for w in chunk)
            f.write(f"{idx}\n")
            f.write(f"{_fmt_ts(start, always_include_hours=True, decimal_marker=',')} --> "
                    f"{_fmt_ts(end, always_include_hours=True, decimal_marker=',')}\n")
            f.write(text + "\n\n")
            idx += 1
    print(f"Wrote {idx-1} cues to {output_srt}")