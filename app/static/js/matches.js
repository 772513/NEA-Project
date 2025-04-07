console.log("JavaScript file loaded successfully");

function confirmDelete(event) {
    // ask for confirmation before submittin the form
    console.log("Confirm delete function triggered");
    const confirmed = confirm("Are you sure you want to delete this match?");
    
    // if the user confirmed, submit the form
    if (!confirmed) {
        // prevent form submission if not confirmed
        event.preventDefault();
        return false;
    }
    return true;
}