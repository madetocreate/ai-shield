const emailPattern = /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g
const phonePattern = /\+?\d[\d\s-]{6,}\d/g

export const maskEmail = (text?: string) => text?.replace(emailPattern, '***@***') ?? ''

export const maskPhone = (text?: string) => text?.replace(phonePattern, '***-****') ?? ''

export const redactPII = (text?: string) => maskPhone(maskEmail(text))

export const redactObject = (input: Record<string, unknown>): Record<string, unknown> => {
  const result: Record<string, unknown> = {}
  Object.entries(input).forEach(([key, value]) => {
    if (typeof value === 'string') {
      result[key] = redactPII(value)
    } else if (Array.isArray(value)) {
      result[key] = value.map((v) => (typeof v === 'string' ? redactPII(v) : v))
    } else {
      result[key] = value
    }
  })
  return result
}

