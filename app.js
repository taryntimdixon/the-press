fetch("daily-latest.json")
  .then(res => res.json())
  .then(data => {

    const container = document.getElementById("articles");

    container.innerHTML = data.articles.map(article => `
      <div style="margin-bottom:30px;padding:15px;background:white;border-radius:10px;">
        <h2>${article.title}</h2>
        <p>${article.summary}</p>
        <p style="color:gray;">Written by Intelligent AI</p>
        <a href="${article.url}">Read article</a>
      </div>
    `).join("");

  })
  .catch(() => {
    document.getElementById("articles").innerHTML =
      "<p>Articles will appear here after the next update.</p>";
  });
