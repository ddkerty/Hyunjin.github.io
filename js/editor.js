class WebPageEditor {
  constructor() {
    // 에디터 페이지에서만 실행
    if (!document.getElementById('editorMode')) {
      return;
    }

    this.editorButton = document.getElementById('editorMode');
    this.pageSelect = document.getElementById('pageSelect');
    this.saveBtn = document.getElementById('saveBtn');
    this.previewFrame = document.getElementById('previewFrame');
    this.addImageBtn = document.getElementById('addImageBtn');
    this.imageUploader = document.getElementById('imageUploader');
    
    // 폰트 편집 관련 요소
    this.fontFamily = document.getElementById('fontFamily');
    this.fontSize = document.getElementById('fontSize');
    this.boldBtn = document.getElementById('boldBtn');
    this.italicBtn = document.getElementById('italicBtn');
    this.underlineBtn = document.getElementById('underlineBtn');
    this.textColor = document.getElementById('textColor');
    
    this.isEditing = false;
    this.currentPage = '';
    this.imageUploadInput = null;
    this.autoSaveInterval = null;
    this.draggedImg = null;

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.createImageUploadInput();
    this.setupFontEditor();
    this.setupToolbarDrag();
    
    // 초기 상태 설정
    this.editorButton.textContent = "편집 모드 활성화";
    this.previewFrame.classList.remove('editing-mode');

    // iframe 로드 이벤트 처리
    this.previewFrame.addEventListener('load', () => {
      this.setupIframeEvents();
    });
  }

  setupEventListeners() {
    // 페이지 선택 이벤트
    this.pageSelect.addEventListener('change', (e) => this.handlePageChange(e));
    
    // 편집 모드 토글
    this.editorButton.addEventListener('click', () => this.toggleEditingMode());
    
    // 저장 버튼 이벤트
    this.saveBtn.addEventListener('click', () => this.saveChanges());
    
    // 이미지 추가 버튼 이벤트
    this.addImageBtn.addEventListener('click', () => this.imageUploader.click());

    // 이미지 업로더 이벤트
    this.imageUploader.addEventListener('change', (e) => this.handleImageUpload(e));
  }

  createImageUploadInput() {
    this.imageUploadInput = document.createElement('input');
    this.imageUploadInput.type = 'file';
    this.imageUploadInput.accept = 'image/*';
    this.imageUploadInput.style.display = 'none';
    document.body.appendChild(this.imageUploadInput);
  }

  handlePageChange(e) {
    const selectedPage = this.pageSelect.value;
    this.currentPage = selectedPage;
    
    // iframe 소스 변경
    this.previewFrame.src = selectedPage;
    
    // 편집 모드 초기화
    this.isEditing = false;
    this.editorButton.textContent = "편집 모드 활성화";
    this.previewFrame.classList.remove('editing-mode');
    this.stopAutoSave();
  }

  handleFrameLoad() {
    if (this.isEditing) {
      this.applyEditingMode(true);
    }
    this.setupImageHandlers();
    
    // 페이지 로드 시 로컬 스토리지에서 불러오기
    this.loadFromLocalStorage();
  }

  toggleEditingMode() {
    this.isEditing = !this.isEditing;
    this.editorButton.textContent = this.isEditing ? "편집 모드 비활성화" : "편집 모드 활성화";
    
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) return;

    // 편집 모드 토글
    if (this.isEditing) {
      previewDoc.body.contentEditable = true;
      this.previewFrame.classList.add('editing-mode');
      this.startAutoSave();
    } else {
      previewDoc.body.contentEditable = false;
      this.previewFrame.classList.remove('editing-mode');
      this.stopAutoSave();
    }

    // 편집 모드가 변경될 때마다 iframe 이벤트 다시 설정
    this.setupIframeEvents();
  }

  applyEditingMode(enable) {
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) return;

    // 텍스트 요소 편집 가능 설정
    const textElements = previewDoc.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, li');
    textElements.forEach(element => {
      element.contentEditable = enable;
      element.classList.toggle('editable', enable);
    });

    // 편집 모드 클래스 토글
    previewDoc.body.classList.toggle('editing-mode', enable);
  }

  setupImageHandlers() {
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) return;

    const images = previewDoc.querySelectorAll('img');
    images.forEach(img => this.setupImageEvents(img));
  }

  setupImageEvents(img) {
    img.setAttribute('draggable', true);

    // 드래그 시작
    img.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', img.src);
      img.classList.add('dragging');
    });

    // 드래그 오버
    img.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    // 드롭
    img.addEventListener('drop', (e) => this.handleImageDrop(e, img));

    // 더블클릭으로 이미지 교체
    img.addEventListener('dblclick', () => this.handleImageDoubleClick(img));
  }

  handleImageDrop(e, targetImg) {
    e.preventDefault();
    const draggedSrc = e.dataTransfer.getData('text/plain');
    const droppedSrc = targetImg.src;
    targetImg.src = draggedSrc;

    const previewDoc = this.getPreviewDocument();
    const draggingImg = previewDoc.querySelector('.dragging');
    if (draggingImg) {
      draggingImg.src = droppedSrc;
      draggingImg.classList.remove('dragging');
    }
  }

  handleImageDoubleClick(img) {
    this.imageUploadInput.click();
    this.imageUploadInput.onchange = () => {
      const file = this.imageUploadInput.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = () => {
        img.src = reader.result;
        // 이미지 크기 조정
        this.adjustImageSize(img);
      };
      reader.readAsDataURL(file);
    };
  }

  adjustImageSize(img) {
    const maxWidth = 800;
    const maxHeight = 600;
    
    if (img.naturalWidth > maxWidth || img.naturalHeight > maxHeight) {
      const ratio = Math.min(maxWidth / img.naturalWidth, maxHeight / img.naturalHeight);
      img.style.width = `${img.naturalWidth * ratio}px`;
      img.style.height = 'auto';
    }
  }

  handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const previewDoc = this.getPreviewDocument();
      if (!previewDoc) return;

      const img = previewDoc.createElement('img');
      img.src = reader.result;
      img.style.position = 'absolute';
      img.style.left = '50px';
      img.style.top = '50px';
      img.style.cursor = 'move';
      img.draggable = true;

      // 드래그 이벤트 설정
      img.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', 'dragging');
        this.draggedImg = img;
      });

      previewDoc.body.appendChild(img);
    };
    reader.readAsDataURL(file);
  }

  saveChanges() {
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) {
      alert("페이지가 아직 로드되지 않았습니다.");
      return;
    }

    const html = previewDoc.documentElement.outerHTML;
    
    // 로컬 스토리지에 저장
    this.saveToLocalStorage(html);
    
    // 파일 다운로드
    this.downloadHTML(html);
  }

  saveToLocalStorage(html) {
    try {
      localStorage.setItem(`editor_${this.currentPage}`, html);
      console.log('로컬 스토리지에 저장되었습니다.');
    } catch (error) {
      console.error('로컬 스토리지 저장 실패:', error);
    }
  }

  loadFromLocalStorage() {
    try {
      const savedHTML = localStorage.getItem(`editor_${this.currentPage}`);
      if (savedHTML) {
        const previewDoc = this.getPreviewDocument();
        if (previewDoc) {
          previewDoc.documentElement.innerHTML = savedHTML;
          console.log('로컬 스토리지에서 불러왔습니다.');
        }
      }
    } catch (error) {
      console.error('로컬 스토리지 로드 실패:', error);
    }
  }

  downloadHTML(html) {
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = this.currentPage;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  startAutoSave() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    
    this.autoSaveInterval = setInterval(() => {
      if (this.isEditing) {
        const previewDoc = this.getPreviewDocument();
        if (previewDoc) {
          const html = previewDoc.documentElement.outerHTML;
          this.saveToLocalStorage(html);
        }
      }
    }, 30000); // 30초마다 자동 저장
  }

  stopAutoSave() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }
  }

  getPreviewDocument() {
    const iframe = this.previewFrame;
    return iframe.contentDocument || iframe.contentWindow.document;
  }

  setupFontEditor() {
    // 폰트 패밀리 변경
    this.fontFamily.addEventListener('change', () => {
      this.applyFontStyle('fontFamily', this.fontFamily.value);
    });

    // 폰트 크기 변경
    this.fontSize.addEventListener('change', () => {
      this.applyFontStyle('fontSize', this.fontSize.value);
    });

    // 굵게
    this.boldBtn.addEventListener('click', () => {
      this.applyFontStyle('bold');
    });

    // 기울임
    this.italicBtn.addEventListener('click', () => {
      this.applyFontStyle('italic');
    });

    // 밑줄
    this.underlineBtn.addEventListener('click', () => {
      this.applyFontStyle('underline');
    });

    // 텍스트 색상
    this.textColor.addEventListener('change', () => {
      this.applyFontStyle('foreColor', this.textColor.value);
    });
  }

  applyFontStyle(command, value = null) {
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) return;

    const selection = previewDoc.getSelection();
    if (!selection.rangeCount) return;

    const range = selection.getRangeAt(0);
    const span = previewDoc.createElement('span');

    switch(command) {
      case 'fontFamily':
        span.style.fontFamily = value;
        break;
      case 'fontSize':
        span.style.fontSize = value + 'px';
        break;
      case 'bold':
        span.style.fontWeight = 'bold';
        break;
      case 'italic':
        span.style.fontStyle = 'italic';
        break;
      case 'underline':
        span.style.textDecoration = 'underline';
        break;
      case 'foreColor':
        span.style.color = value;
        break;
    }

    range.surroundContents(span);
    selection.removeAllRanges();
  }

  setupToolbarDrag() {
    const toolbar = document.getElementById('toolbar');
    let isDragging = false;
    let offsetX, offsetY;

    toolbar.addEventListener('mousedown', (e) => {
      isDragging = true;
      offsetX = e.clientX - toolbar.getBoundingClientRect().left;
      offsetY = e.clientY - toolbar.getBoundingClientRect().top;
    });

    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        toolbar.style.left = `${e.clientX - offsetX}px`;
        toolbar.style.top = `${e.clientY - offsetY}px`;
      }
    });

    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  setupIframeEvents() {
    const previewDoc = this.getPreviewDocument();
    if (!previewDoc) return;

    // iframe 내부의 모든 버튼에 이벤트 리스너 추가
    const buttons = previewDoc.querySelectorAll('button');
    buttons.forEach(button => {
      button.addEventListener('click', (e) => {
        // 버튼의 원래 동작을 유지하면서 편집 모드 상태를 확인
        if (this.isEditing) {
          e.preventDefault();
          alert('편집 모드에서는 버튼을 클릭할 수 없습니다. 편집 모드를 비활성화하세요.');
        }
      });
    });

    // 링크 클릭 이벤트 처리
    const links = previewDoc.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        if (this.isEditing) {
          e.preventDefault();
          alert('편집 모드에서는 링크를 클릭할 수 없습니다. 편집 모드를 비활성화하세요.');
        }
      });
    });
  }
}

// 에디터 페이지에서만 초기화
if (document.getElementById('editorMode')) {
  document.addEventListener('DOMContentLoaded', () => {
    new WebPageEditor();
  });
}
  