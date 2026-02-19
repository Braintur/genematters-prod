# HTML Article Support Guide

## Overview

Articles are now rendered as **HTML content**, allowing you to format articles with rich formatting including headers, lists, emphasis, and more.

## How It Works

1. When creating/editing an article, enter HTML code in the content field
2. The content is stored as-is in the database
3. When viewing the article, the HTML is rendered in the browser
4. The `|safe` filter in Jinja2 ensures the HTML is displayed correctly

## Basic HTML Tags

### Paragraphs
```html
<p>This is a paragraph.</p>
```

### Headings
```html
<h1>Main Title</h1>
<h2>Section Title</h2>
<h3>Subsection</h3>
```

### Text Formatting
```html
<strong>Bold text</strong>
<em>Italic text</em>
<u>Underlined text</u>
<mark>Highlighted text</mark>
```

### Lists

**Unordered List:**
```html
<ul>
    <li>First item</li>
    <li>Second item</li>
    <li>Third item</li>
</ul>
```

**Ordered List:**
```html
<ol>
    <li>First step</li>
    <li>Second step</li>
    <li>Third step</li>
</ol>
```

### Links
```html
<a href="https://example.com">Click here</a>
```

### Blockquotes
```html
<blockquote>
    This is a quote or important information.
</blockquote>
```

### Line Breaks
```html
<br>
```

## Full Article Example

```html
<h2>Introduction</h2>
<p>This is the introduction to the article. You can include as much text as you want.</p>

<h3>First Section</h3>
<p>Here's some content for the first section:</p>
<ul>
    <li>Point one</li>
    <li>Point two</li>
    <li>Point three</li>
</ul>

<h3>Second Section</h3>
<p>More content here. You can make text <strong>bold</strong> or <em>italic</em>.</p>

<blockquote>
    A famous quote goes here.
</blockquote>

<p>For more information, <a href="https://example.com">visit this link</a>.</p>
```

## Advanced HTML

### Code Blocks
```html
<pre><code>
function example() {
    console.log("Hello, World!");
}
</code></pre>
```

### Inline Code
```html
<code>function_name()</code>
```

### Horizontal Rule
```html
<hr>
```

### Line Breaks in Multiple Paragraphs
```html
<p>First paragraph.</p>
<p>Second paragraph after a break.</p>
```

## Images

### Inserting Images

When you upload an image, you can insert it into your article. Images are automatically provided with default sizing styles.

**Default image tag (automatically inserted):**
```html
<img src="https://cdn.example.com/image.jpg" alt="Article image" style="width: 100%; height: auto;">
```

### Resizing Images

You can easily adjust image size using the `style` attribute with percentages:

**Full width (default):**
```html
<img src="image.jpg" alt="description" style="width: 100%; height: auto;">
```

**Half width:**
```html
<img src="image.jpg" alt="description" style="width: 50%; height: auto;">
```

**75% width:**
```html
<img src="image.jpg" alt="description" style="width: 75%; height: auto;">
```

**Fixed size with max-width:**
```html
<img src="image.jpg" alt="description" style="width: 400px; height: auto;">
```

### Centering Images

To center an image, wrap it in a paragraph with center alignment:
```html
<p style="text-align: center;">
    <img src="image.jpg" alt="description" style="width: 75%; height: auto;">
</p>
```

### Image Sizing Tips

- **`width: 100%;`** - Image takes full container width
- **`height: auto;`** - Maintains aspect ratio (recommended)
- **Use percentages** (1-100%) for responsive sizing
- **Common sizes:**
  - `50%` - Half width (good for side-by-side layouts)
  - `75%` - Three-quarters width
  - `33%` - One-third width (for galleries)

## Styling Available

Articles automatically inherit the following styles:

- **Font**: Clean, readable serif font
- **Colors**: Black text on white background
- **Spacing**: Comfortable margins and padding between elements
- **Links**: Colored with accent color, underlined
- **Lists**: Properly indented and formatted
- **Blockquotes**: Left-bordered in accent color

## Tips

✅ **Do:**
- Keep formatting clean and consistent
- Use semantic HTML tags
- Test your HTML before saving large articles
- Use lists for step-by-step instructions
- Use blockquotes for important information

❌ **Don't:**
- Mix too many formatting styles
- Use very deep nesting
- Override styles with inline CSS (won't work)
- Use old HTML (use `<strong>` instead of `<b>`)

## HTML Security

The system uses Jinja2's `|safe` filter to render HTML. The content is **not sanitized**, so:

⚠️ **Important**: Only trusted administrators should create articles. The system assumes article contributors are trustworthy users.

For production deployments with untrusted user contributions, consider implementing HTML sanitization with a library like `bleach` or `nh3`.

## Copying Content from Other Sources

If copying articles from Word, Google Docs, or web pages:

1. Export as HTML or plain text
2. Copy the content
3. Paste into the article form
4. Clean up any unnecessary formatting
5. Apply consistent formatting as needed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HTML not rendering | Make sure tags are properly closed |
| Formatting looks weird | Check for unclosed tags or conflicting styles |
| Links don't work | Use full URLs: `https://example.com` |
| Special characters broken | Use HTML entities: `&amp;`, `&lt;`, `&gt;`, `&quot;` |

## Examples

### News Article Format
```html
<h2>Breaking News: Article Title</h2>
<p><em>Published: February 19, 2026</em></p>

<p>Lead paragraph with the most important information.</p>

<h3>Details</h3>
<p>More detailed information goes here.</p>

<p>Additional context and supporting details.</p>

<h3>What's Next</h3>
<ul>
    <li>Future development 1</li>
    <li>Future development 2</li>
</ul>
```

### Tutorial Format
```html
<h2>How to Use Feature X</h2>
<p>This tutorial will teach you how to use Feature X effectively.</p>

<h3>Step 1: Getting Started</h3>
<p>First, do this...</p>
<code>example code here</code>

<h3>Step 2: Main Process</h3>
<p>Next, follow these steps:</p>
<ol>
    <li>Action one</li>
    <li>Action two</li>
    <li>Action three</li>
</ol>

<h3>Conclusion</h3>
<p>You've now learned how to use Feature X!</p>
```
