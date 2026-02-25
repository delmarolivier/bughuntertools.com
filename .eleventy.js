module.exports = function(eleventyConfig) {
  // Copy static assets
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("sitemap.xml");
  eleventyConfig.addPassthroughCopy("VALIDATED_PRODUCTS.md");

  // Date formatting filter — used in templates
  eleventyConfig.addFilter("dateString", function(date) {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  });

  // Create articles collection
  eleventyConfig.addCollection("articles", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/*.njk")
      .filter(item => !item.inputPath.includes("index.njk")) // Exclude index page
      .sort((a, b) => {
        // Sort by date, newest first
        return new Date(b.data.date) - new Date(a.data.date);
      });
  });

  // Create demos collection (SecurityClaw Demo Content Series)
  eleventyConfig.addCollection("demos", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/demos/*.njk")
      .filter(item => !item.inputPath.includes("index.njk")) // Exclude index page
      .sort((a, b) => {
        // Sort by date, newest first
        return new Date(b.data.date) - new Date(a.data.date);
      });
  });

  // Input/output directories
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_layouts"
      // _data is at src/_data/ by default (relative to input)
    },
    templateFormats: ["html", "md", "njk"],
    htmlTemplateEngine: "njk"
  };
};
