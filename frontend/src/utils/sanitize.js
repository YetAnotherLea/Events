import DOMPurify from "dompurify";

// Les descriptions viennent d'OpenAgenda (contenu tiers) : on ne garde que la mise en forme
export const sanitizeHtml = (html) =>
  DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["br", "p", "ul", "ol", "li", "strong", "em", "b", "i", "a"],
    ALLOWED_ATTR: ["href"],
  });
