var requestIsActive = false;

function showPopup() {
    document.querySelector('.overlay').style.display = 'block';
    document.querySelector('.popup').style.display = 'block';
}

function hidePopup(event) {
    if (event.target === document.querySelector('.overlay')) {
        document.querySelector('.overlay').style.display = 'none';
        document.querySelector('.popup').style.display = 'none';
    }
}

document.querySelector(".popup form").addEventListener('submit', function(event){
    event.preventDefault();
    hidePopup(event);
    document.querySelector(".popup input[type='submit']").disabled = true;

    var loadingMessage = document.createElement("p");
    loadingMessage.textContent = "Carregando...";
    document.querySelector(".popup").appendChild(loadingMessage);

    window.removeEventListener('beforeunload', beforeUnloadHandler);

    event.target.submit();

    window.addEventListener('beforeunload', beforeUnloadHandler);
});

function beforeUnloadHandler(e) {
    if (requestIsActive) {
        var confirmationMessage = "Uma requisição ainda está em processo. Realmente reseja sair?";
        e.returnValue = confirmationMessage;
        return confirmationMessage;
    }
}
window.addEventListener('beforeunload', beforeUnloadHandler);

function showWorkspacePopup() {
    var workspaceBtn = document.querySelector('.btn[onclick="showWorkspacePopup()"]');
    workspaceBtn.disabled = true; 
    document.querySelector('.workspace-popup').style.display = 'block';

    setTimeout(function() {
        document.querySelector('.workspace-popup').style.display = 'none';
        document.querySelector("#loading").style.display = "block";
    }, 2000);

    fetch("/download-workspaces")
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.blob();
    })
    .then(blob => {
        document.querySelector("#loading").style.display = "none";
        workspaceBtn.disabled = false;
    })
    .catch(error => {
        console.log("There was a problem with the fetch operation:", error.message);
        document.querySelector("#loading").style.display = "none";
        workspaceBtn.disabled = false;
    });
}

function showReportFormPopup() {
    document.querySelector('#reportFormPopup').style.display = 'block';
}

function closeReportFormPopup() {
    document.querySelector('#reportFormPopup').style.display = 'none';
}

function submitReportForm() {
    const reportName = document.querySelector('input[name="report_name"]').value;
    const reportNamesArray = reportName.split(',').map(item => item.trim()); // Split by comma and remove any spaces

    if (!reportName) {
        alert("Digite o nome do curso");
        return;
    }

    if (reportNamesArray.length > 10) {
        alert("Só é possível baixar 10 relatórios por vez.");
        return;
    }
}
