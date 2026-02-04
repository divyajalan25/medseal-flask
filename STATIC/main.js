const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("report");
const statusText = document.getElementById("statusText");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const patientId = document.getElementById("patient_id").value;

    if (!fileInput.files.length) {
        alert("Select a file first");
        return;
    }

    statusText.innerText = "⏳ Uploading & hashing...";
    resultDiv.innerHTML = "";

    const formData = new FormData();
    formData.append("report", fileInput.files[0]);
    formData.append("patient_id", patientId);

    try {
        const response = await fetch("/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        statusText.innerText = data.status;

        if (data.uploaded_at) {
            resultDiv.innerHTML = `
                <p><b>Uploaded At:</b> ${data.uploaded_at}</p>
                ${data.filename ? `<p><b>File:</b> ${data.filename}</p>` : ""}
                ${data.hash ? `<p><b>Hash:</b> ${data.hash}</p>` : ""}
            `;
        }

    } catch (err) {
        statusText.innerText = "❌ Error occurred";
    }
});