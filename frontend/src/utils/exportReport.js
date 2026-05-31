import { saveAs } from 'file-saver'
import { 
  Document, Packer, Paragraph, TextRun, HeadingLevel, 
  Table, TableRow, TableCell, BorderStyle, WidthType 
} from 'docx'
import pdfMake from 'pdfmake/build/pdfmake'
import pdfFonts from 'pdfmake/build/vfs_fonts'

// Initialize pdfMake fonts
pdfMake.vfs = pdfFonts.pdfMake ? pdfFonts.pdfMake.vfs : pdfFonts.vfs

const DISCLAIMER = 'This report is synthesized from a deterministic simulation run using synthetic personas. It is designed for manuscript stress testing and structural analysis, not absolute market validation. No real social platforms or external user accounts were contacted. Local models run completely offline to preserve privacy.'

function getFormatDate() {
  return new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
}

/**
 * Helper to download a string blob.
 */
function downloadBlob(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType })
  saveAs(blob, filename)
}

/**
 * 1. Generate JSON Export
 */
export function generateJson(report, sessionContext) {
  if (!report) return
  const exportPayload = {
    _meta: {
      exported_at: getFormatDate(),
      project_name: report.title || sessionContext.projectId,
      disclaimer: DISCLAIMER
    },
    ...report
  }
  const dataStr = JSON.stringify(exportPayload, null, 2)
  downloadBlob(dataStr, `swarmbook_report_${sessionContext.projectId || 'demo'}.json`, 'application/json')
}

/**
 * 2. Generate Markdown String
 */
export function buildMarkdownContent(report, sessionContext) {
  if (!report) return ''
  const lines = []
  
  lines.push(`# Swarmbook Report: ${report.title || report.project_id}`)
  lines.push(`*Generated at: ${getFormatDate()}*`)
  lines.push('')
  lines.push(`- **Project ID**: \`${report.project_id}\``)
  lines.push(`- **Report ID**: \`${report.report_id}\``)
  if (report.privacy_mode) lines.push(`- **Privacy Mode**: \`${report.privacy_mode}\``)
  if (report.draft_id || report.version) {
    lines.push(`- **Draft**: \`${report.draft_id || 'unknown'}\` / \`${report.version || 'unknown'}\``)
  }
  lines.push('')
  
  lines.push('## Executive Summary')
  lines.push(report.summary || 'No summary available.')
  lines.push('')
  lines.push(`**Stage Confidence**: ${Math.round((report.confidence || 0) * 100)}%`)
  lines.push('')
  
  lines.push('## Scorecard Metrics')
  const keys = ['rating_distribution', 'dnf', 'controversy', 'viral', 'quoteability', 'polarization']
  for (const key of keys) {
    const payload = (report.scorecard || {})[key] || {}
    const score = payload.score
    const risk = payload.risk || payload.dnf_risk || payload.controversy_risk || payload.polarization_score || payload.quoteability_score
    const headline = score !== undefined ? score : risk
    if (headline === undefined || headline === null) continue
    const band = payload.confidence_band ? ` [Low: ${payload.confidence_band.low}, High: ${payload.confidence_band.high}]` : ''
    lines.push(`- **${key.toUpperCase().replace(/_/g, ' ')}**: ${headline}${band}`)
  }
  
  lines.push('')
  lines.push('## Revision Priorities')
  if (report.scorecard?.revision_priority?.ranked_items?.length) {
    for (const item of report.scorecard.revision_priority.ranked_items) {
      lines.push(`### ${item.item_type.toUpperCase()}: ${item.item_id} (Score: ${item.priority_score})`)
      lines.push(`*Reasons*: ${item.reasons.join(', ')}`)
      if (item.evidence_refs && item.evidence_refs.length) {
        lines.push(`*Evidence*: ${item.evidence_refs.join(', ')}`)
      }
      lines.push('')
    }
  } else {
    lines.push('- No revision priorities were generated.')
  }
  
  lines.push('')
  lines.push('## Limitations & Caveats')
  lines.push(`> ${DISCLAIMER}`)
  
  return lines.join('\n')
}

export function generateMarkdown(report, sessionContext) {
  const content = buildMarkdownContent(report, sessionContext)
  if (content) {
    downloadBlob(content, `swarmbook_report_${sessionContext.projectId || 'demo'}.md`, 'text/markdown')
  }
}

/**
 * 3. Copy to Clipboard (full Markdown report)
 */
export async function copyToClipboard(report, sessionContext) {
  const content = buildMarkdownContent(report, sessionContext)
  if (!content) throw new Error('No report content available to copy.')
  
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(content)
  } else {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = content
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
  }
}

/**
 * 6. Copy Executive Summary to Clipboard
 * Copies the executive verdict + confidence + top metrics as plain text.
 */
export async function copyExecutiveSummary(report) {
  if (!report) throw new Error('No report available.')
  const rating = report.scorecard?.rating_distribution?.predicted_mean_rating
  const dnf = report.scorecard?.dnf?.dnf_risk
  const conf = Math.round((report.confidence || 0) * 100)
  const lines = [
    `EXECUTIVE SUMMARY — ${report.title || report.project_id}`,
    `Generated: ${getFormatDate()}`,
    ``,
    report.summary || 'No summary available.',
    ``,
    `Stage Confidence: ${conf}%`,
    rating !== undefined ? `Predicted Mean Rating: ${Number(rating).toFixed(2)} ★` : '',
    dnf !== undefined ? `DNF Risk: ${Math.round(Number(dnf) * 100)}%` : '',
    ``,
    `[Synthesized by Swarmbook Studio — synthetic simulation only, not market validation]`
  ].filter(l => l !== undefined).join('\n')

  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(lines)
  } else {
    const ta = document.createElement('textarea')
    ta.value = lines
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}

/**
 * 7. Copy Revision Plan to Clipboard
 * Copies all ranked revision items as a numbered plain-text checklist.
 */
export async function copyRevisionPlan(report) {
  if (!report) throw new Error('No report available.')
  const items = report.scorecard?.revision_priority?.ranked_items || []
  const lines = [
    `REVISION PLAN — ${report.title || report.project_id}`,
    `Generated: ${getFormatDate()}`,
    ``
  ]
  if (items.length === 0) {
    lines.push('No revision priorities were generated.')
  } else {
    items.forEach((item, idx) => {
      lines.push(`${idx + 1}. [${item.item_type.toUpperCase()}] ${item.item_id} — Priority Score: ${Math.round(item.priority_score * 100)}%`)
      if (item.reasons?.length) {
        item.reasons.forEach(r => lines.push(`   • ${r}`))
      }
      if (item.evidence_refs?.length) {
        lines.push(`   Evidence: ${item.evidence_refs.join(', ')}`)
      }
      lines.push('')
    })
  }
  lines.push(`[Synthesized by Swarmbook Studio — synthetic simulation only, not market validation]`)

  const text = lines.join('\n')
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text)
  } else {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}


/**
 * 4. Generate DOCX Export (Structured)
 */
export async function generateDocx(report, sessionContext) {
  if (!report) return

  const children = []
  
  // Title
  children.push(new Paragraph({
    text: `Swarmbook Report: ${report.title || report.project_id}`,
    heading: HeadingLevel.TITLE,
    spacing: { after: 400 }
  }))
  
  // Meta
  children.push(new Paragraph({
    text: `Generated at: ${getFormatDate()} | Project ID: ${report.project_id} | Draft: ${report.draft_id || 'unknown'}`,
    spacing: { after: 400 }
  }))
  
  // Executive Summary
  children.push(new Paragraph({ text: 'Executive Summary', heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 } }))
  children.push(new Paragraph({ text: report.summary || 'No summary available.', spacing: { after: 200 } }))
  children.push(new Paragraph({ text: `Stage Confidence: ${Math.round((report.confidence || 0) * 100)}%`, spacing: { after: 400 } }))

  // Revision Priorities
  children.push(new Paragraph({ text: 'Revision Priorities', heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 } }))
  
  if (report.scorecard?.revision_priority?.ranked_items?.length) {
    for (const item of report.scorecard.revision_priority.ranked_items) {
      children.push(new Paragraph({ 
        text: `Target: ${item.item_type.toUpperCase()}:${item.item_id} (Score: ${item.priority_score})`, 
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 } 
      }))
      children.push(new Paragraph({
        children: [new TextRun({ text: 'Reasons: ', bold: true }), new TextRun(item.reasons.join(', '))]
      }))
    }
  } else {
    children.push(new Paragraph({ text: 'No revision priorities were ranked.' }))
  }

  // Limitations
  children.push(new Paragraph({ text: 'Limitations & Caveats', heading: HeadingLevel.HEADING_1, spacing: { before: 600, after: 200 } }))
  children.push(new Paragraph({ text: DISCLAIMER, italics: true }))

  const doc = new Document({
    sections: [{
      properties: {},
      children: children
    }]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, `swarmbook_report_${sessionContext.projectId || 'demo'}.docx`)
}

/**
 * 5. Generate PDF Export (Structured via PDFMake)
 */
export function generatePdf(report, sessionContext) {
  if (!report) return

  const docDefinition = {
    content: [
      { text: `Swarmbook Report`, style: 'title' },
      { text: report.title || report.project_id, style: 'subtitle' },
      { text: `Generated: ${getFormatDate()} | Project: ${report.project_id}`, style: 'meta', margin: [0, 0, 0, 40] },
      
      { text: 'Executive Verdict', style: 'header' },
      { text: report.summary || 'No summary available.', margin: [0, 0, 0, 10] },
      { text: `Stage Confidence: ${Math.round((report.confidence || 0) * 100)}%`, margin: [0, 0, 0, 30] },
      
      { text: 'Revision Priorities', style: 'header' }
    ],
    styles: {
      title: { fontSize: 24, bold: true, alignment: 'center', margin: [0, 40, 0, 10] },
      subtitle: { fontSize: 18, italics: true, alignment: 'center', margin: [0, 0, 0, 10] },
      meta: { fontSize: 10, color: 'gray', alignment: 'center' },
      header: { fontSize: 16, bold: true, margin: [0, 20, 0, 10] },
      subheader: { fontSize: 14, bold: true, margin: [0, 10, 0, 5] },
      italics: { italics: true, color: 'gray' }
    },
    defaultStyle: {
      fontSize: 11,
      lineHeight: 1.4
    }
  }

  if (report.scorecard?.revision_priority?.ranked_items?.length) {
    for (const item of report.scorecard.revision_priority.ranked_items) {
      docDefinition.content.push({ text: `Target: ${item.item_type.toUpperCase()}:${item.item_id} (Score: ${item.priority_score})`, style: 'subheader' })
      docDefinition.content.push({ text: `Reasons: ${item.reasons.join(', ')}`, margin: [0, 0, 0, 10] })
    }
  } else {
    docDefinition.content.push({ text: 'No revision priorities were ranked.', margin: [0, 0, 0, 20] })
  }

  // Limitations at end
  docDefinition.content.push({ text: 'Limitations & Caveats', style: 'header', margin: [0, 40, 0, 10] })
  docDefinition.content.push({ text: DISCLAIMER, style: 'italics' })

  pdfMake.createPdf(docDefinition).download(`swarmbook_report_${sessionContext.projectId || 'demo'}.pdf`)
}
