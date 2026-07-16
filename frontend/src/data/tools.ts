import { Tool } from '../types';
import { 
  Combine, 
  Scissors, 
  RotateCw, 
  Minimize2, 
  Image as ImageIcon, 
  Images, 
  Lock, 
  Unlock,
  FileText,
  Presentation,
  TableProperties,
  PenTool,
  Type,
  FileMinus,
  Files,
  LayoutGrid,
  Scan,
  Wrench,
  FileSearch,
  FileCode,
  FileArchive,
  Hash,
  Droplets,
  Crop,
  FormInput,
  Eraser,
  GitCompare,
  Bot,
  Languages,
  FileCode2,
  MessageSquare
} from 'lucide-react';

export const TOOLS: Tool[] = [
  // --- ORGANIZE PDF ---
  {
    id: 'merge',
    name: 'Merge PDF',
    description: 'Combine PDFs in the order you want with the easiest PDF merger available.',
    category: 'organize',
    icon: Combine,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: true,
    apiEndpoint: '/api/tools/merge'
  },
  {
    id: 'split',
    name: 'Split PDF',
    description: 'Separate one page or a whole set for easy conversion into independent PDF files.',
    category: 'organize',
    icon: Scissors,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/split',
    options: [
      {
        name: 'ranges',
        label: 'Pages to split (e.g. 1-3,5 or "all")',
        type: 'text',
        defaultValue: 'all'
      }
    ]
  },
  {
    id: 'remove-pages',
    name: 'Remove pages',
    description: 'Remove pages from a PDF document in a flash.',
    category: 'organize',
    icon: FileMinus,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/remove-pages',
    options: [
      {
        name: 'pages',
        label: 'Pages to remove (e.g. 1,3-5)',
        type: 'text',
        defaultValue: ''
      }
    ]
  },
  {
    id: 'extract-pages',
    name: 'Extract pages',
    description: 'Extract pages from your PDF file into a new document.',
    category: 'organize',
    icon: Files,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/extract-pages',
    options: [
      {
        name: 'pages',
        label: 'Pages to extract (e.g. 1,3-5)',
        type: 'text',
        defaultValue: ''
      }
    ]
  },
  {
    id: 'organize-pdf',
    name: 'Organize PDF',
    description: 'Sort, add and delete PDF pages. Drag and drop the page thumbnails.',
    category: 'organize',
    icon: LayoutGrid,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/organize-pdf'
  },
  {
    id: 'scan-to-pdf',
    name: 'Scan to PDF',
    description: 'Capture document scans from your mobile device or scanner and turn them into PDF.',
    category: 'organize',
    icon: Scan,
    acceptedTypes: { 'image/*': ['.jpg', '.jpeg', '.png'] },
    multiFile: true,
    apiEndpoint: '/api/tools/scan-to-pdf'
  },

  // --- OPTIMIZE PDF ---
  {
    id: 'compress',
    name: 'Compress PDF',
    description: 'Reduce file size while optimizing for maximal PDF quality.',
    category: 'optimize',
    icon: Minimize2,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/compress',
    options: [
      {
        name: 'level',
        label: 'Compression Level',
        type: 'select',
        defaultValue: 'recommended',
        choices: [
          { value: 'low', label: 'Low (High Quality)' },
          { value: 'recommended', label: 'Recommended' },
          { value: 'extreme', label: 'Extreme (Lowest Quality)' }
        ]
      }
    ]
  },
  {
    id: 'repair-pdf',
    name: 'Repair PDF',
    description: 'Repair a damaged PDF and recover data from corrupt PDF.',
    category: 'optimize',
    icon: Wrench,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/repair-pdf'
  },
  {
    id: 'ocr-pdf',
    name: 'OCR PDF',
    description: 'Make your scanned PDF searchable and selectable.',
    category: 'optimize',
    icon: FileSearch,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/ocr-pdf'
  },

  // --- CONVERT TO PDF ---
  {
    id: 'jpg-to-pdf',
    name: 'JPG to PDF',
    description: 'Convert JPG images to PDF in seconds. Easily adjust orientation and margins.',
    category: 'convert',
    icon: Images,
    acceptedTypes: { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] },
    multiFile: true,
    apiEndpoint: '/api/tools/jpg-to-pdf'
  },
  {
    id: 'word-to-pdf',
    name: 'WORD to PDF',
    description: 'Make DOC and DOCX files easy to read by converting them to PDF.',
    category: 'convert',
    icon: FileText,
    acceptedTypes: { 'application/msword': ['.doc'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    multiFile: true,
    apiEndpoint: '/api/tools/word-to-pdf'
  },
  {
    id: 'powerpoint-to-pdf',
    name: 'POWERPOINT to PDF',
    description: 'Make PPT and PPTX slideshows easy to view by converting them to PDF.',
    category: 'convert',
    icon: Presentation,
    acceptedTypes: { 'application/vnd.ms-powerpoint': ['.ppt'], 'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'] },
    multiFile: true,
    apiEndpoint: '/api/tools/powerpoint-to-pdf'
  },
  {
    id: 'excel-to-pdf',
    name: 'EXCEL to PDF',
    description: 'Convert EXCEL spreadsheets to PDF documents with columns adjusted to the page width.',
    category: 'convert',
    icon: TableProperties,
    acceptedTypes: { 'application/vnd.ms-excel': ['.xls'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] },
    multiFile: true,
    apiEndpoint: '/api/tools/excel-to-pdf'
  },
  {
    id: 'html-to-pdf',
    name: 'HTML to PDF',
    description: 'Convert webpages in HTML to PDF. Copy and paste the URL or upload your HTML files.',
    category: 'convert',
    icon: FileCode,
    acceptedTypes: { 'text/html': ['.html'] },
    multiFile: false,
    apiEndpoint: '/api/tools/html-to-pdf'
  },

  // --- CONVERT FROM PDF ---
  {
    id: 'pdf-to-jpg',
    name: 'PDF to JPG',
    description: 'Extract all images contained in a PDF or convert each page to a JPG file.',
    category: 'convert',
    icon: ImageIcon,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-jpg',
    options: [
      {
        name: 'dpi',
        label: 'Image Quality (DPI)',
        type: 'select',
        defaultValue: '150',
        choices: [
          { value: '72', label: '72 DPI (Web)' },
          { value: '150', label: '150 DPI (Print)' },
          { value: '300', label: '300 DPI (High Res)' }
        ]
      }
    ]
  },
  {
    id: 'pdf-to-word',
    name: 'PDF to Word',
    description: 'Easily convert your PDF files into easy to edit DOCX documents.',
    category: 'convert',
    icon: FileText,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-word'
  },
  {
    id: 'pdf-to-powerpoint',
    name: 'PDF to PowerPoint',
    description: 'Turn your PDF files into easy to edit PPTX slideshows.',
    category: 'convert',
    icon: Presentation,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-powerpoint'
  },
  {
    id: 'pdf-to-excel',
    name: 'PDF to Excel',
    description: 'Pull data straight from PDFs into Excel spreadsheets.',
    category: 'convert',
    icon: TableProperties,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-excel'
  },
  {
    id: 'pdf-to-pdfa',
    name: 'PDF to PDF/A',
    description: 'Convert your PDF to PDF/A for long-term archiving.',
    category: 'convert',
    icon: FileArchive,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-pdfa'
  },

  // --- EDIT PDF ---
  {
    id: 'rotate',
    name: 'Rotate PDF',
    description: 'Rotate your PDFs the way you need them.',
    category: 'edit',
    icon: RotateCw,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/rotate',
    options: [
      {
        name: 'angle',
        label: 'Rotation Angle',
        type: 'select',
        defaultValue: '90',
        choices: [
          { value: '90', label: '90° Clockwise' },
          { value: '180', label: '180°' },
          { value: '270', label: '90° Counter-clockwise' }
        ]
      }
    ]
  },
  {
    id: 'add-page-numbers',
    name: 'Add page numbers',
    description: 'Add page numbers into PDFs with ease. Choose your positions, dimensions, typography.',
    category: 'edit',
    icon: Hash,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/add-page-numbers'
  },
  {
    id: 'add-watermark',
    name: 'Add watermark',
    description: 'Stamp an image or text over your PDF in seconds. Choose the typography, transparency and position.',
    category: 'edit',
    icon: Droplets,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/add-watermark'
  },
  {
    id: 'crop-pdf',
    name: 'Crop PDF',
    description: 'Trim PDF margins, change PDF page size.',
    category: 'edit',
    icon: Crop,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/crop-pdf'
  },
  {
    id: 'edit',
    name: 'Edit PDF',
    description: 'Add text annotations anywhere on your PDF document.',
    category: 'edit',
    icon: Type,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/edit'
  },
  {
    id: 'pdf-forms',
    name: 'PDF Forms',
    description: 'Fill in PDF forms. Create PDF forms.',
    category: 'edit',
    icon: FormInput,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-forms'
  },

  // --- PDF SECURITY ---
  {
    id: 'unlock',
    name: 'Unlock PDF',
    description: 'Remove PDF password security, giving you the freedom to use your PDFs as you want.',
    category: 'security',
    icon: Unlock,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/unlock',
    options: [
      {
        name: 'password',
        label: 'Current Password',
        type: 'text',
        defaultValue: ''
      }
    ]
  },
  {
    id: 'protect',
    name: 'Protect PDF',
    description: 'Encrypt your PDF with a password to keep sensitive data secure.',
    category: 'security',
    icon: Lock,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/protect',
    options: [
      {
        name: 'password',
        label: 'Set Password',
        type: 'text',
        defaultValue: ''
      }
    ]
  },
  {
    id: 'sign-pdf',
    name: 'Sign PDF',
    description: 'Sign yourself or request electronic signatures from others.',
    category: 'security',
    icon: PenTool,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/sign-pdf'
  },
  {
    id: 'redact-pdf',
    name: 'Redact PDF',
    description: 'Permanently remove visible text and graphics from a document.',
    category: 'security',
    icon: Eraser,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/redact-pdf'
  },
  {
    id: 'compare-pdf',
    name: 'Compare PDF',
    description: 'Compare two PDFs and easily highlight the differences.',
    category: 'security',
    icon: GitCompare,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: true,
    apiEndpoint: '/api/tools/compare-pdf'
  },

  // --- PDF INTELLIGENCE ---
  {
    id: 'ai-summarizer',
    name: 'AI Summarizer',
    description: 'Summarize your PDF content quickly with AI.',
    category: 'intelligence',
    icon: Bot,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/ai-summarizer'
  },
  {
    id: 'translate-pdf',
    name: 'Translate PDF',
    description: 'Translate documents to any language while maintaining layout.',
    category: 'intelligence',
    icon: Languages,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/translate-pdf'
  },
  {
    id: 'pdf-to-markdown',
    name: 'PDF to Markdown',
    description: 'Convert PDF content directly to Markdown format for easy editing.',
    category: 'intelligence',
    icon: FileCode2,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-markdown'
  },
  {
    id: 'doc-talk',
    name: 'Doc Talk',
    description: 'Chat with your PDF. Ask questions and get answers directly from your document.',
    category: 'intelligence',
    icon: MessageSquare,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/doc-talk'
  }
];
