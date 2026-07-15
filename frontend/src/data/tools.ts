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
  Type
} from 'lucide-react';

export const TOOLS: Tool[] = [
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
    id: 'rotate',
    name: 'Rotate PDF',
    description: 'Rotate your PDFs the way you need them. You can even rotate multiple PDFs at once.',
    category: 'organize',
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
    id: 'pdf-to-word',
    name: 'PDF to Word',
    description: 'Easily convert your PDF files into easy to edit DOCX documents. Converted Word documents are almost 100% accurate.',
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
    description: 'Pull data straight from PDFs into Excel spreadsheets in a few short seconds.',
    category: 'convert',
    icon: TableProperties,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-excel'
  },
  {
    id: 'pdf-to-pages',
    name: 'PDF to Pages',
    description: 'Instantly convert your PDF into a document that Apple Pages can open natively on Mac or iOS.',
    category: 'convert',
    icon: PenTool,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/pdf-to-pages'
  },
  {
    id: 'edit',
    name: 'Edit PDF',
    description: 'Add text annotations anywhere on your PDF document.',
    category: 'edit' as any,
    icon: Type,
    acceptedTypes: { 'application/pdf': ['.pdf'] },
    multiFile: false,
    apiEndpoint: '/api/tools/edit'
  }
];
