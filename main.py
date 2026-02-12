import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post


# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="wide"
)

LENGTH_OPTIONS = ["Short", "Medium", "Long"]
LANGUAGE_OPTIONS = ["English", "Hinglish", "Tanglish"]


@st.cache_resource
def load_fs():
    return FewShotPosts()


def format_examples(examples):
    """Nicely format few-shot examples for display."""
    out = []
    for i, ex in enumerate(examples, start=1):
        out.append(f"**Example {i}**\n\n{ex.get('text','')}")
    return "\n\n---\n\n".join(out)


def main():
    st.title("💼 LinkedIn Post Generator")
    st.caption("Style-guided generation using your curated dataset (few-shot prompting).")

    fs = load_fs()
    tags = sorted(fs.get_tags())

    # -----------------------------
    # Sidebar controls
    # -----------------------------
    with st.sidebar:
        st.header("Controls")
        selected_tag = st.selectbox("Topic", options=tags)
        selected_length = st.selectbox("Length", options=LENGTH_OPTIONS, index=1)
        selected_language = st.selectbox("Language", options=LANGUAGE_OPTIONS, index=0)

        num_variants = st.selectbox("Generate variants", options=[1, 2, 3], index=2)
        show_examples = st.checkbox("Show examples used", value=True)
        use_custom_idea = st.checkbox("Provide a custom idea", value=False)

    # Optional idea input (makes app feel “real”)
    idea = ""
    if use_custom_idea:
        idea = st.text_area(
            "Your idea / context (optional but recommended)",
            placeholder="e.g., My experience being ghosted after interviews + lesson learned..."
        )

    # -----------------------------
    # Main action
    # -----------------------------
    colA, colB = st.columns([1, 1])
    with colA:
        st.info(f"**Topic:** {selected_tag}  |  **Length:** {selected_length}  |  **Language:** {selected_language}")

    with colB:
        generate_clicked = st.button("🚀 Generate", use_container_width=True)

    if generate_clicked:
        with st.spinner("Generating post(s)..."):
            results = []

            for _ in range(num_variants):
                # ✅ Preferred: generate_post returns (post_text, examples)
                # Fallback: if it returns only text, we handle that too.
                out = generate_post(selected_length, selected_language, selected_tag, idea=idea)

                if isinstance(out, tuple) and len(out) == 2:
                    post_text, examples_used = out
                else:
                    post_text, examples_used = out, None

                results.append((post_text, examples_used))

        st.success("Done ✅")

        # -----------------------------
        # Display results
        # -----------------------------
        if num_variants == 1:
            post_text, examples_used = results[0]
            st.subheader("Generated Post")
            st.write(post_text)

            st.download_button(
                "⬇️ Download as .txt",
                data=post_text,
                file_name="linkedin_post.txt",
                mime="text/plain"
            )

            if show_examples and examples_used:
                with st.expander("📌 Examples used (few-shot)"):
                    st.markdown(format_examples(examples_used))

        else:
            tabs = st.tabs([f"Variant {i+1}" for i in range(num_variants)])
            for i, tab in enumerate(tabs):
                with tab:
                    post_text, examples_used = results[i]
                    st.subheader(f"Variant {i+1}")
                    st.write(post_text)

                    st.download_button(
                        f"⬇️ Download Variant {i+1}",
                        data=post_text,
                        file_name=f"linkedin_post_variant_{i+1}.txt",
                        mime="text/plain"
                    )

                    if show_examples and examples_used:
                        with st.expander("📌 Examples used (few-shot)"):
                            st.markdown(format_examples(examples_used))

    # -----------------------------
    # Small footer
    # -----------------------------
    st.divider()
    st.caption("Built with Streamlit + LangChain + Groq + LLaMA • Portfolio demo")


if __name__ == "__main__":
    main()
