const API_URL = 'https://livohealth-backend.onrender.com';
const input = document.getElementById('imageInput');
const zone = document.getElementById('dropzone');
const button = document.getElementById('analyzeBtn');
const status = document.getElementById('status');
const result = document.getElementById('result');
const preview = document.getElementById('preview');
let file = null;
let previewUrl = null;
function setFile(next) {
  result.classList.add('hidden');
  status.textContent = '';
  file = null;
  button.disabled = true;
  if (!next) return;
  if (!['image/jpeg','image/png'].includes(next.type)) { status.textContent = 'Please select a JPG or PNG image.'; return; }
  if (next.size > 10 * 1024 * 1024) { status.textContent = 'Image must be under 10 MB.'; return; }
  file = next;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(next);
  preview.src = previewUrl;
  document.getElementById('filename').textContent = next.name;
  document.getElementById('previewWrap').classList.remove('hidden');
  button.disabled = false;
}
input.addEventListener('change', () => setFile(input.files[0]));
zone.addEventListener('dragover', e => {e.preventDefault(); zone.classList.add('drag');});
zone.addEventListener('dragleave', () => zone.classList.remove('drag'));
zone.addEventListener('drop', e => {e.preventDefault(); zone.classList.remove('drag'); setFile(e.dataTransfer.files[0]);});
button.addEventListener('click', async () => {
  if (!file) return;
  button.disabled = true;
  result.classList.add('hidden');
  status.textContent = 'Analyzing image…';
  const form = new FormData();
  form.append('file', file);
  try {
    const response = await fetch(`${API_URL}/predict`, {method:'POST', body:form});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Analysis failed.');
    document.getElementById('prediction').textContent = `Model-selected class: ${data.predicted_class}`;
    const h = (data.hcc_model_score * 100).toFixed(1);
    const b = (data.hemangioma_model_score * 100).toFixed(1);
    document.getElementById('hccScore').textContent = `${h}%`;
    document.getElementById('hemScore').textContent = `${b}%`;
    document.getElementById('hccBar').style.width = `${h}%`;
    document.getElementById('hemBar').style.width = `${b}%`;
    result.classList.remove('hidden');
    status.textContent = 'Analysis completed. Research output only.';
  } catch (err) { status.textContent = `Error: ${err.message}. Confirm the FastAPI backend is running.`; }
  finally {button.disabled = false;}
});
