function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('MyDatabase', 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('cacheStore')) {
                db.createObjectStore('cacheStore', { keyPath: 'filePath' });
            }
        };

        request.onsuccess = (event) => resolve(event.target.result);
        request.onerror = (event) => reject(event.target.error);
    });
}

async function getRepoModifiedStatus(repo_owner, repo_name) {
    const ModifiedDate = localStorage.getItem(`${repo_owner}/${repo_name}/ModifiedDate`);

    if (ModifiedDate) {
        const requestOptions = {
            method: "GET",
            headers: { "If-Modified-Since": ModifiedDate }
        };

        const response = await fetch(`https://api.github.com/repos/${repo_owner}/${repo_name}/contents`, requestOptions);
        if (response.status === 200) {
            localStorage.setItem(`${repo_owner}/${repo_name}/ModifiedDate`, response.headers.get("Last-Modified"));
            return true;
        }
        return false;
    }

    localStorage.setItem(`${repo_owner}/${repo_name}/ModifiedDate`, new Date().toUTCString());
    return true;
}

async function preloadData(repo_owner, repo_name, innerApiUrl) {
    try {
        if (!await getRepoModifiedStatus(repo_owner, repo_name)) {
            console.log("No changes in repo");
            return;
        }

        console.log("Preloading data");
        const db = await openDatabase();
        const response = await fetch(innerApiUrl);
        const data = await response.json();

        const transaction = db.transaction('cacheStore', 'readwrite');
        const store = transaction.objectStore('cacheStore');

        for (const [fileName, content] of Object.entries(data)) {
            const filePath = `${repo_owner}/${repo_name}/${fileName}`;
            store.put({ filePath, content });
        }

        await new Promise((resolve, reject) => {
            transaction.oncomplete = resolve;
            transaction.onerror = () => reject(transaction.error);
            transaction.onabort = () => reject(transaction.error);
        });

        console.log('Transaction completed successfully.');
    } catch (error) {
        console.error('Error while preloading data:', error);
    }
}

async function getData(fileName, repo_owner) {
    try {
        const db = await openDatabase();
        const transaction = db.transaction('cacheStore', 'readonly');
        const store = transaction.objectStore('cacheStore');
        const filePath = `${repo_owner}/${fileName}`;

        return new Promise((resolve, reject) => {
            const request = store.get(filePath);
            request.onsuccess = () => resolve(request.result ? request.result.content : null);
            request.onerror = (event) => reject(event.target.error);
        });
    } catch (error) {
        console.error('Error while opening database:', error);
        throw error;
    }
}

function setupFileListeners(repo_owner, repo_name) {
    document.querySelectorAll(".file").forEach(file => {
        file.addEventListener("dblclick", async () => {
            const filePath = file.nextElementSibling.value;
            try {
                let data = await getData(filePath, repo_owner);
                if (!data) {
                    const response = await fetch(`https://api.github.com/repos/${repo_owner}/${repo_name}/contents/${filePath.split("/").slice(1).join("/")}`);
                    data = atob((await response.json()).content);
                }

                const codeTag = document.getElementById("code");
                codeTag.innerHTML = data;
                codeTag.classList = [];
                hljs.highlightAll();
            } catch (error) {
                console.error('Error while getting data:', error);
            }
        });
    });
}

function setupFolderListeners() {
    document.querySelectorAll(".folder").forEach(folder => {
        folder.addEventListener("click", () => {
            const childUl = folder.nextElementSibling;
            if (childUl) {
                childUl.style.display = childUl.style.display === "none" ? "block" : "none";
                childUl.style.marginLeft = "15px";
            }
        });
    });
}

function setupFormListeners() {
    document.getElementById("prompt-form").addEventListener("submit", async function (event) {
        event.preventDefault();
        const description = document.getElementById("description").value;
        if (!description) return;

        const selectedCheckboxes = document.querySelectorAll(".dynamic-checkbox:checked");
        const values = Array.from(selectedCheckboxes).map(checkbox => checkbox.value.split("/").slice(1).join("/"));
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        const response = await fetch(this.action, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ description, selected_files: JSON.stringify(values), repo_id: repoID })
        });

        const answer = await response.json();
        const codeTag = document.getElementById("code");
        codeTag.innerHTML = marked.parse(Object.values(answer)[0]);
        codeTag.classList = ["hljs", "language-markdown"];
        hljs.highlightAll();
    });
}

function setupQuestionListeners() {
    document.querySelectorAll(".question-wrapper").forEach(quest => {
        quest.addEventListener("click", async () => {
            const questionID = quest.getAttribute("question-id");
            const response = await fetch(`${questionDetailUrl}?question_id=${questionID}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            });

            const answer = await response.json();
            document.getElementById("description").value = answer.prompt;
            document.getElementById("code").innerHTML = marked.parse(answer.answer);
            document.querySelectorAll(".dynamic-checkbox").forEach(box => {
                box.checked = answer.files_context.includes(box.value.split("/").slice(1).join("/"));
            });
            const codeTag = document.getElementById("code");
            codeTag.classList = ["hljs language-markdown"];
        });
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    setupFileListeners(repo_owner, repo_name);
    setupFolderListeners();
    setupFormListeners();
    setupQuestionListeners();
    await preloadData(repo_owner, repo_name, innerApiUrl);
});
