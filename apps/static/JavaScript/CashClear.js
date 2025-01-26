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

function cleverClearCash(repo_owner, repo_name, selectedBranchName){
    console.log("Clever Clear Cash")
    const CLEAR_CASH_INTERVAL = 60*60*24*7;
    const ls = localStorage;
    const ls_ClearCashKey = `${repo_owner}/${repo_name}/${selectedBranchName}/ClearCashDate`
    const ls_ModifiedDate = `${repo_owner}/${repo_name}/${selectedBranchName}/ModifiedDate`
    const ls_date = ls.getItem(ls_ClearCashKey);
    if(ls_date){
        const lastCleared = new Date(ls_date);
        const now = new Date();
        if(now - lastCleared >= CLEAR_CASH_INTERVAL){
            console.log("Clearing cash");
            // open indexed db and clear rows that key starts with  {repo_owner}/${repo_name}/${selectedBranchName}

            openDatabase().then((db) => {
                const transaction = db.transaction('cacheStore', 'readwrite');
                const store = transaction.objectStore('cacheStore');
                const request = store.openCursor();

                request.onsuccess = (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        if (cursor.key.startsWith(`${repo_owner}/${repo_name}/${selectedBranchName}`)) {
                            store.delete(cursor.key);
                        }
                        cursor.continue();
                    }
                };

                request.onerror = (event) => {
                    console.error('Error clearing cache:', event.target.error);
                };
            }).catch((error) => {
                console.error('Failed to open database:', error);
            });

            ls.removeItem(ls_ClearCashKey);
            ls.setItem(ls_ClearCashKey, new Date().toUTCString());
            ls.removeItem(ls_ModifiedDate);
        }
        else{
            console.log("Not clearing cash");
        }
    }
    else{
        console.log("Setting clear cash date");
        ls.setItem(ls_ClearCashKey, new Date().toUTCString());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cleverClearCash(repo_owner, repo_name, selectedBranchName);
})