# 🛡️ DevChat v2.0: Secure Encrypted Messenger

**DevChat** is a real-time, secure chat application built with **Python** and **Streamlit**. It demonstrates advanced implementation of **Symmetric Encryption**, **Key Derivation**, and **Local Data Persistence**.

Designed as a secure communication tool where "Privacy is Default."

---

## 🚀 Key Features

### 🔒 Military-Grade Encryption
*   **Fernet (AES-128-CBC):** Every message is encrypted before it leaves the memory.
*   **HMAC-SHA256:** Ensures message integrity (tamper-proofing).
*   **Unique IVs:** Initialization Vectors ensure that identical messages produce different encrypted strings.

### 🔑 Advanced Key Management
*   **PBKDF2 (Password-Based Key Derivation):** Users can access rooms using a simple password. The app mathematically derives a cryptographic key from this password using **SHA-256** and **Salt**.
*   **Manual Key Support:** Option to use raw Fernet keys for higher entropy requirements.

### ⚡ Performance & Storage
*   **SQLite Database:** Migrated from CSV to SQLite to handle concurrent writes and ensure ACID compliance.
*   **Real-Time Updates:** Uses Streamlit's `@st.fragment` for auto-refreshing chat windows without reloading the entire page.

---

## 🛠️ Tech Stack

*   **Language:** Python 3.10+
*   **Frontend:** Streamlit (Custom CSS & Fragments)
*   **Cryptography:** `cryptography` library (Hazmat primitives)
*   **Database:** SQLite3
*   **Data Handling:** Pandas

---

## 💻 How to Run Locally

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/DevChat.git
    cd DevChat
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

4.  **Login & Chat**
    *   Enter a **Username**.
    *   Choose a **Channel** (e.g., #General).
    *   Set a **Room Password** (e.g., "MySecretPass").
    *   Start chatting!

---

## 📸 Security Demonstration

The app includes a **Debug / Audit Mode**. Toggling this reveals the raw data stored in the database.

**Example:**
*   **Decrypted View:** `Hello World`
*   **Database View:** `gAAAAABk9... (Ciphertext)`

This proves that even if the database file (`devchat.db`) is stolen, the attacker sees only gibberish without the password.

---

## 👤 Author

**Jann Elijah Limpiado**
*   *IT Student*

---

⚠️ **Disclaimer:** This project is for educational and portfolio purposes. While it uses standard cryptographic primitives, it is not intended for high-stakes classified communications.
