document.querySelectorAll(".message-top").forEach(message => {
    setTimeout(() => {
        message.remove();
    }, 3500);
});