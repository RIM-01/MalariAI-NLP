# 1. INSTALL LIBRARIES
!pip install -q groq gradio torchvision

# --- 2. BACKEND SETUP ---
try:
    GROQ_KEY = userdata.get('GROQ_API_KEY')
    client = Groq(api_key=GROQ_KEY)
except:
    print("⚠️ Please add 'GROQ_API_KEY' to Colab Secrets!")

    def explain_diagnosis(species, confidence_str):
    if not species: return "Error: No diagnosis found."
    prompt = (
        f"You are a Senior Pathologist. The CNN detected **{species}** ({confidence_str}). "
        "Briefly explain the visual morphological characteristics (ring stage, chromatin dots, gametocyte shape, etc.) "
        "that justify this diagnosis in a Giemsa smear."
    )
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=350
        )
        return completion.choices[0].message.content
    except: return "AI connection failed."

def llama_chat(message, history):
    messages = [{"role": "system", "content": "You are a Malaria Expert."}]
    for m in history: messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": message})
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages, temperature=0.7, max_tokens=512
        )
        return completion.choices[0].message.content
    except: return "AI Error."