document.querySelectorAll(".message").forEach(message => {
    setTimeout(() => {
        message.remove();
    }, 3500);
});