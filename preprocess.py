import json
from llm import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


# -----------------------------
# Fix for Windows/emoji issues:
# removes invalid surrogate chars that break UTF-8 encoding
# -----------------------------
def clean_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return s.encode("utf-8", "surrogatepass").decode("utf-8", "ignore")


def extract_metadata(post: str) -> dict:
    template = """
You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.

Rules:
1. Return a valid JSON only. No preamble, no markdown.
2. JSON object must have exactly three keys: line_count, language, tags.
3. tags is an array of text tags. Extract maximum two tags.
4. language must be one of: English, Hinglish, Tanglish
   - Hinglish means Hindi + English (written in English letters)
   - Tanglish means Tamil + English (written in English letters)

Post:
{post}
""".strip()

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke({"post": post})

    # Parse LLM output as JSON
    try:
        parser = JsonOutputParser()
        return parser.parse(response.content)
    except OutputParserException as e:
        # Show raw output for debugging
        raise OutputParserException(
            f"Metadata JSON parse failed. Raw output:\n{response.content}"
        ) from e


def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post.get("tags", []))

    tags_str = ", ".join(sorted(t.strip() for t in unique_tags if isinstance(t, str) and t.strip()))

    template = """
I will give you a list of tags. You need to unify tags with the following requirements:

1. Tags are unified and merged to create a shorter list.
   Example 1: "Jobseekers", "Job Hunting" can be merged into "Job Search".
   Example 2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation".
   Example 3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement".
   Example 4: "Scam Alert", "Job Scam" can be mapped to "Scams".

2. Each unified tag should follow Title Case convention. Example: "Motivation", "Job Search".
3. Output should be a JSON object only. No preamble, no markdown.
4. Output should have mapping of original tag and the unified tag.
   For example: {{"Jobseekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

Here is the list of tags:
{tags}
""".strip()

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke({"tags": tags_str})

    try:
        json_parser = JsonOutputParser()
        return json_parser.parse(response.content)
    except OutputParserException as e:
        raise OutputParserException(f"Unable to parse unified tags JSON. Raw output:\n{response.content}") from e

def process_posts(raw_file_path: str, processed_file_path: str):
    # Load raw posts
    with open(raw_file_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    enriched_posts = []

    # Enrich each post
    for i, post in enumerate(posts):
        try:
            text_clean = clean_text(post.get("text", ""))
            metadata = extract_metadata(text_clean)

            # Merge original + metadata (works in Python 3.9+)
            post_with_metadata = {**post, **metadata}
            post_with_metadata["text"] = text_clean  # store cleaned text

            enriched_posts.append(post_with_metadata)

        except Exception as e:
            print("\n Failed while processing post index:", i)
            print("Text preview (repr):", repr(post.get("text", ""))[:300])
            print("Error:", type(e).__name__, "-", str(e))
            raise

    # Unify tags
    unified_map = get_unified_tags(enriched_posts)

    # Apply unified tags safely (no KeyError)
    for post in enriched_posts:
        current_tags = post.get("tags", [])
        normalized = set()
        for t in current_tags:
            t = t.strip() if isinstance(t, str) else str(t)
            normalized.add(unified_map.get(t, t))  # fallback to original if missing
        post["tags"] = sorted(normalized)

    # Save output (preserve emojis)
    with open(processed_file_path, "w", encoding="utf-8") as out:
        json.dump(enriched_posts, out, indent=4, ensure_ascii=False)

    print(f"\n Done Saved: {processed_file_path}")


if __name__ == "__main__":
    process_posts("data/post.json", "data/processed_posts.json")