// Initialize PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

let currentPdfFile = null;
let sheets = [{ id: 1, name: "시트 1", pages: [] }];
let activeSheetId = 1;
let sheetIdCounter = 1;

let totalPdfPages = 0;
let isDragging = false;
let dragMode = null; // 'select' or 'deselect'

const uploadInput = document.getElementById('pdf-upload');
const generateBtn = document.getElementById('generate-btn');
const previewContainer = document.getElementById('pdf-preview-container');
const loadingMsg = document.getElementById('loading-msg');
const settingsPanel = document.getElementById('settings-panel');
const docTitleInput = document.getElementById('doc-title');
const selectionControls = document.getElementById('selection-controls');
const selectAllBtn = document.getElementById('select-all-btn');
const deselectAllBtn = document.getElementById('deselect-all-btn');

// Multi-Sheet UI elements
const tabsContainer = document.getElementById('tabs-container');
const addSheetBtn = document.getElementById('add-sheet-btn');
const deleteSheetBtn = document.getElementById('delete-sheet-btn');
const activeSheetNameInput = document.getElementById('active-sheet-name');

// ---------------------------------
// SHEET MANAGEMENT LOGIC
// ---------------------------------
function renderTabs() {
    tabsContainer.innerHTML = '';
    sheets.forEach(sheet => {
        const tab = document.createElement('div');
        tab.className = `tab ${sheet.id === activeSheetId ? 'active' : ''}`;
        tab.innerText = sheet.name;
        tab.addEventListener('click', () => {
            activeSheetId = sheet.id;
            activeSheetNameInput.value = sheet.name;
            renderTabs();
            updateVisualSelection();
        });
        tabsContainer.appendChild(tab);
    });
    
    // Disable delete if only 1 sheet
    deleteSheetBtn.disabled = sheets.length <= 1;
}

addSheetBtn.addEventListener('click', () => {
    sheetIdCounter++;
    const newSheet = { id: sheetIdCounter, name: `시트 ${sheets.length + 1}`, pages: [] };
    sheets.push(newSheet);
    activeSheetId = newSheet.id;
    activeSheetNameInput.value = newSheet.name;
    renderTabs();
    updateVisualSelection();
});

deleteSheetBtn.addEventListener('click', () => {
    if (sheets.length <= 1) return;
    sheets = sheets.filter(s => s.id !== activeSheetId);
    activeSheetId = sheets[0].id;
    activeSheetNameInput.value = sheets[0].name;
    renderTabs();
    updateVisualSelection();
});

activeSheetNameInput.addEventListener('input', (e) => {
    const sheet = sheets.find(s => s.id === activeSheetId);
    if(sheet) {
        sheet.name = e.target.value.trim() || '이름 없음';
        renderTabs();
    }
});

// ---------------------------------
// PDF AND UX LOGIC
// ---------------------------------
document.addEventListener('mouseup', () => {
    isDragging = false;
    dragMode = null;
});

uploadInput.addEventListener('change', async (e) => {
    currentPdfFile = e.target.files[0];
    if (!currentPdfFile) return;

    if (currentPdfFile.type !== 'application/pdf') {
        alert('PDF 파일만 업로드 가능합니다.');
        return;
    }

    // Reset state
    sheets = [{ id: 1, name: "시트 1", pages: [] }];
    activeSheetId = 1;
    sheetIdCounter = 1;
    activeSheetNameInput.value = "시트 1";
    renderTabs();
    
    docTitleInput.value = currentPdfFile.name.replace('.pdf', '');
    settingsPanel.classList.remove('hidden');
    selectionControls.classList.add('hidden');
    updateGenerateButton();
    previewContainer.innerHTML = '';
    loadingMsg.classList.remove('hidden');

    try {
        const fileReader = new FileReader();
        fileReader.onload = async function() {
            const typedarray = new Uint8Array(this.result);
            const pdf = await pdfjsLib.getDocument(typedarray).promise;
            totalPdfPages = pdf.numPages;
            
            loadingMsg.classList.add('hidden');
            selectionControls.classList.remove('hidden');
            renderPDFPages(pdf);
        };
        fileReader.readAsArrayBuffer(currentPdfFile);
    } catch (err) {
        console.error(err);
        loadingMsg.classList.add('hidden');
        alert("PDF 렌더링 중 오류가 발생했습니다.");
    }
});

async function renderPDFPages(pdf) {
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const unscaledViewport = page.getViewport({ scale: 1.0 });
        const scale = 400 / unscaledViewport.width;
        const viewport = page.getViewport({ scale: scale });
        
        const wrapper = document.createElement('div');
        wrapper.className = 'page-wrapper';
        wrapper.dataset.pageIndex = pageNum - 1; // 0-indexed
        wrapper.id = `page-wrapper-${pageNum - 1}`;
        
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = { canvasContext: context, viewport: viewport };
        await page.render(renderContext).promise;
        
        const label = document.createElement('div');
        label.className = 'page-label';
        label.innerText = `페이지 ${pageNum}`;
        
        wrapper.appendChild(canvas);
        wrapper.appendChild(label);
        
        // Mouse interactions
        wrapper.addEventListener('mousedown', (e) => {
            e.preventDefault();
            isDragging = true;
            const pageIndex = parseInt(wrapper.dataset.pageIndex);
            const activeSheetPages = sheets.find(s => s.id === activeSheetId).pages;
            
            if (activeSheetPages.includes(pageIndex)) {
                dragMode = 'deselect';
                removeSelection(pageIndex);
            } else {
                dragMode = 'select';
                addSelection(pageIndex);
            }
        });

        wrapper.addEventListener('mouseenter', () => {
            if (!isDragging) return;
            const pageIndex = parseInt(wrapper.dataset.pageIndex);
            const activeSheetPages = sheets.find(s => s.id === activeSheetId).pages;
            if (dragMode === 'select' && !activeSheetPages.includes(pageIndex)) {
                addSelection(pageIndex);
            } else if (dragMode === 'deselect' && activeSheetPages.includes(pageIndex)) {
                removeSelection(pageIndex);
            }
        });
        
        previewContainer.appendChild(wrapper);
    }
}

function addSelection(pageIndex) {
    const activeSheetPages = sheets.find(s => s.id === activeSheetId).pages;
    if (!activeSheetPages.includes(pageIndex)) {
        activeSheetPages.push(pageIndex);
        updateVisualSelection();
    }
}

function removeSelection(pageIndex) {
    const activeSheetPages = sheets.find(s => s.id === activeSheetId).pages;
    const idx = activeSheetPages.indexOf(pageIndex);
    if (idx !== -1) {
        activeSheetPages.splice(idx, 1);
        updateVisualSelection();
    }
}

function updateVisualSelection() {
    // Clear all visuals
    document.querySelectorAll('.page-wrapper').forEach(wrapper => {
        wrapper.classList.remove('selected', 'other-sheet');
        wrapper.removeAttribute('data-order');
    });
    
    // Apply styling based on sheet assignments
    sheets.forEach(sheet => {
        sheet.pages.forEach((pageIndex, i) => {
            const wrapper = document.getElementById(`page-wrapper-${pageIndex}`);
            if (wrapper) {
                if (sheet.id === activeSheetId) {
                    wrapper.classList.remove('other-sheet');
                    wrapper.classList.add('selected');
                    wrapper.setAttribute('data-order', i + 1);
                } else {
                    // Only apply other-sheet if it's not currently selected in active sheet (handles dupes)
                    if (!wrapper.classList.contains('selected')) {
                        wrapper.classList.add('other-sheet');
                    }
                }
            }
        });
    });
    
    updateGenerateButton();
}

selectAllBtn.addEventListener('click', () => {
    const activeSheetPages = sheets.find(s => s.id === activeSheetId).pages;
    activeSheetPages.length = 0;
    for(let i=0; i<totalPdfPages; i++) {
        activeSheetPages.push(i);
    }
    updateVisualSelection();
});

deselectAllBtn.addEventListener('click', () => {
    sheets.find(s => s.id === activeSheetId).pages.length = 0;
    updateVisualSelection();
});

function updateGenerateButton() {
    const totalSelected = sheets.reduce((sum, sheet) => sum + sheet.pages.length, 0);
    if (totalSelected > 0 && currentPdfFile) {
        generateBtn.disabled = false;
        generateBtn.innerText = `총 ${totalSelected}장 (멀티 시트) 넘버스로 변환하기`;
    } else {
        generateBtn.disabled = true;
        generateBtn.innerText = '선택된 시트/페이지가 없습니다';
    }
}

generateBtn.addEventListener('click', async () => {
    const totalSelected = sheets.reduce((sum, sheet) => sum + sheet.pages.length, 0);
    if (totalSelected === 0 || !currentPdfFile) return;

    const docName = docTitleInput.value.trim() || '생성완료_문서';
    
    // Prepare cleanly formatted payload corresponding to backend requirements
    const sheetsPayload = sheets.map(s => ({
        name: s.name,
        pages: s.pages
    }));
    
    const formData = new FormData();
    formData.append('file', currentPdfFile);
    formData.append('sheets_data', JSON.stringify(sheetsPayload));
    formData.append('doc_name', docName);
    
    generateBtn.disabled = true;
    generateBtn.innerText = "서버에서 변환 중입니다...";

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        if (!response.ok) throw new Error("서버 에러");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${docName}.numbers`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (err) {
        console.error(err);
        alert("변환 중 오류가 발생했습니다. 백엔드 콘솔을 확인해주세요.");
    } finally {
        updateGenerateButton();
    }
});
