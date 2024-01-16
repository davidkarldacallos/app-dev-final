$(document).ready(function () {
    // Function to add a new choice item
    function addChoiceItem() {
        var defaultText = 'Default Choice';
        var newItem = $('<div class="choice-item">' +
            '<span class="choice-text">' + defaultText + '</span>' +
            '<button type="button" class="btn btn-sm btn-primary edit-choice" title="Edit Choice">' +
            '<i class="fas fa-pencil-alt"></i>' +
            '</button>' +
            '<button type="button" class="btn btn-sm btn-danger remove-choice" title="Remove Choice">' +
            '<i class="fas fa-trash-alt"></i>' +
            '</button>' +
            '</div>');
        newItem.appendTo('#choices-container');

        var hiddenInput = $('<input type="hidden" name="choices[]" value="' + defaultText + '">');
        hiddenInput.appendTo(newItem);
    }

    // Event listener for adding a new choice item
    $('#add-choice').on('click', function () {
        addChoiceItem();
    });

    // Event listener for removing a choice item
    $(document).on('click', '.remove-choice', function () {
        $(this).closest('.choice-item').remove();
    });

    // Event listener for editing a choice item
    $(document).on('click', '.edit-choice', function () {
        var choiceItem = $(this).closest('.choice-item');
        var currentText = choiceItem.find('.choice-text').text();
        var newText = prompt('Edit the choice:', currentText);

        // Update the choice text if the user provided a new text
        if (newText !== null) {
            choiceItem.find('.choice-text').text(newText);

            var hiddenInput = choiceItem.find('input[type="hidden"]');
            hiddenInput.val(newText);
        }
    });
});