{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BG Info Document Data",
  "description": "JSON schema for the structured data consumed by generate_bg_doc.py",
  "type": "object",
  "required": ["company_name", "overview", "strategic_context", "sources"],
  "properties": {
    "company_name": {
      "type": "string",
      "description": "Full legal or trading name of the company"
    },
    "overview": {
      "type": "string",
      "description": "1-2 paragraphs: HQ, revenue, market position, listed status, division structure"
    },
    "strategic_context": {
      "type": "string",
      "description": "Why this company is relevant to the user's platform/technology"
    },
    "strategic_image": {
      "type": "string",
      "description": "Absolute path to an investor-slide PNG or JPG (optional)"
    },
    "strategic_image_caption": {
      "type": "string",
      "description": "Caption for the strategic image"
    },
    "divisions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "description", "brands", "revenue"],
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "brands": { "type": "string" },
          "revenue": { "type": "string" }
        }
      }
    },
    "brands": {
      "type": "object",
      "description": "Map of category -> list of brand descriptions",
      "additionalProperties": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "financials": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["year", "metrics"],
        "properties": {
          "year": { "type": "string" },
          "metrics": {
            "type": "object",
            "description": "Arbitrary metric keys (e.g. Revenue, EBITDA, EPS)",
            "additionalProperties": { "type": "string" }
          }
        }
      }
    },
    "alternative_proteins": {
      "type": "object",
      "description": "Precision fermentation / alt-protein layout",
      "properties": {
        "public_statements": {
          "type": "array",
          "items": { "type": "string" },
          "description": "CEO/CSO quotes, CMD/AR slides"
        },
        "initiatives": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Internal business units or R&D programmes"
        },
        "partnerships": {
          "type": "array",
          "items": { "type": "string" },
          "description": "JVs, licensing deals, research partnerships"
        },
        "investments": {
          "type": "array",
          "items": { "type": "string" },
          "description": "VC/CVC bets, venture investments"
        },
        "ma_deals": {
          "type": "array",
          "items": { "type": "string" },
          "description": "M&A deals in the alt-protein / PF space"
        }
      }
    },
    "ma_transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["year", "target", "amount", "description"],
        "properties": {
          "year": { "type": "string" },
          "target": { "type": "string" },
          "amount": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    },
    "innovation": {
      "type": "object",
      "properties": {
        "open_innovation": { "type": "string" },
        "relevant_products": { "type": "string" },
        "pf_stance": { "type": "string" },
        "collaboration_hook": { "type": "string" }
      }
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["url"],
        "properties": {
          "label": { "type": "string" },
          "url": { "type": "string", "format": "uri" }
        }
      }
    }
  }
}
