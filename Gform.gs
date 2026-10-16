function createMarianYouthVigilForm() {
  // 1. Initialize the Google Form
  var form = FormApp.create('Marian Youth Vigil 2026 - Official Group Registration');
  
  var formDescription = 
    'Official Group Registration Form for the Marian Youth Vigil 2026, to be held on September 7–8, 2026, at Pilgrims Center - Minor Basilica of Our Lady of the Rosary of Manaoag\n\n' +
    'This form must be completed by the Delegation Head ONLY.\n' +
    'Only ONE comprehensive submission is permitted per parish delegation\n\n' +
    'Registration and Form Editing Deadline: August 15, 2026, at 11:59 PM\n\n' +
    'Maximum delegation size: 1 Delegation Head + 29 Participants\n' +
    'You may return to your submitted form to:\n' +
    '- Replace a participant\n' +
    '- Update participant information (e.g., Name or contact details)\n' +
    'After the deadline, the form will be closed and no further edits will be accepted.\n' +
    '___\n' +
    'Data Privacy Notice: In compliance with the Data Privacy Act of 2012 (RA 10173), all personal information collected in this form will be used strictly by the Vicariate Social Communications and the Marian Youth Vigil 2026 Organizing Committee for delegation registration, event logistics, safety protocols, and official communications. By submitting this form, you certify that as the Delegation Head, you have obtained explicit consent from all listed participants (and guardians, if applicable) to share their information, which will be securely stored, kept confidential, and safely disposed of following the event.';
  
  form.setDescription(formDescription);

  form.setCollectEmail(true);
  form.setLimitOneResponsePerUser(true);
  form.setAllowResponseEdits(true);

  // ---------------------------------------------------------------------
  // Reusable validators
  // ---------------------------------------------------------------------
  var PHONE_PATTERN = '^(09\\d{9}|\\+63\\d{10})$'; // e.g. 09171234567 or +639171234567

  function phoneValidation() {
    return FormApp.createTextValidation()
        .setHelpText('Enter a valid PH mobile number, e.g. 09171234567 or +639171234567')
        .requireTextMatchesPattern(PHONE_PATTERN)
        .build();
  }

  function ageValidation() {
    return FormApp.createTextValidation()
        .setHelpText('Enter a whole number between 1 and 100')
        .requireNumberBetween(1, 100)
        .build();
  }

  function addParticipantFields(labelPrefix, required) {
    form.addTextItem()
        .setTitle(labelPrefix + ' Full Name')
        .setRequired(required)
        .setHelpText('e.g., Juan Dela Cruz');

    form.addTextItem()
        .setTitle(labelPrefix + ' Nickname')
        .setRequired(required)
        .setHelpText('e.g., Jun');

    form.addTextItem()
        .setTitle(labelPrefix + ' Age')
        .setRequired(required)
        .setValidation(ageValidation());

    form.addListItem()
        .setTitle(labelPrefix + ' T-Shirt Size')
        .setChoiceValues(['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL'])
        .setRequired(required);
  }

  // ---------------------------------------------------------------------
  // 2. Section 1: Vicariate Selection & Delegation Head Details
  // ---------------------------------------------------------------------
  var vicariateQuestion = form.addMultipleChoiceItem()
      .setTitle('Select Your Vicariate')
      .setRequired(true);

  form.addSectionHeaderItem()
      .setTitle('Delegation Head Information')
      .setHelpText('The Delegation Head serves as the official representative of your delegation throughout the Marian Youth Vigil.');

  form.addTextItem()
      .setTitle('Delegation Head Contact Number')
      .setRequired(true)
      .setValidation(phoneValidation());

  // Delegation Head fields (required)
  addParticipantFields('Delegation Head', true);

  // ---------------------------------------------------------------------
  // 3. Define the 9 Vicariates and their matching Parishes
  // ---------------------------------------------------------------------
  var archdioceseData = [
    {
      name: "Vicariate of St. Vincent Ferrer",
      parishes: [
        "Santo Domingo Ybañez de Erquicia Parish",
        "Archdiocesan Shrine of St. Vincent Ferrer",
        "Saint Catherine of Siena Parish",
        "Saint John the Baptist Parish",
        "San Lorenzo Ruiz Parish",
        "Mary Help of Christians Parish",
        "San Isidro Labrador Parish"
      ]
    },
    {
      name: "Vicariate of Sts. Peter and Paul",
      parishes: [
        "Saints Peter and Paul Parish",
        "Cristo Divino Tesoro Parish",
        "Our Lady of Fatima Parish",
        "St. Joseph of Nazareth Parish",
        "Santuario de Santa Barbara Holy Family Parish",
        "St. Joseph the Worker Parish",
        "San Isidro a Dumaralos Parish"
      ]
    },
    {
      name: "Vicariate of St. John the Evangelist",
      parishes: [
        "St. Michael the Archangel Parish",
        "St. Louis-Marie Grignion de Montfort Parish",
        "Most Holy Rosary Parish",
        "St. Therese of the Child Jesus Parish",
        "St. John the Evangelist Cathedral Parish",
        "Annunciation of the Lord Parish",
        "St. Gabriel the Archangel Parish"
      ]
    },
    {
      name: "Vicariate of Our Lady of the Rosary Manaoag",
      parishes: [
        "Our Lady of the Rosary Parish",
        "St. Joseph the Patriarch Parish",
        "Holy Cross Parish",
        "Our Lady of the Blessed Sacrament Parish"
      ]
    },
    {
      name: "Vicariate of Saint Dominic de Guzman",
      parishes: [
        "Saint Francis Gil de Federich Chaplaincy",
        "Our Lady of Consolation Parish",
        "Saint John Paul II Parish",
        "Our Lady of Lourdes Pastoral Station",
        "Saint Pius V Parish",
        "San Padre Pio Parish",
        "Most Holy Trinity Parish",
        "Minor Basilica of Saint Dominic de Guzman Parish",
        "Holy Family Parish",
        "St. Joseph, Husband of Mary Parish",
        "San Pedro Calungsod Parish"
      ]
    },
    {
      name: "Vicariate of St. Ildephonse",
      parishes: [
        "Our Mother of Perpetual Help Parish",
        "San Antonio de Padua Parish",
        "Jesus the Nazarene Pastoral Station",
        "Saint Francis of Assisi Parish",
        "St. Ildephonse Parish"
      ]
    },
    {
      name: "Vicariate of Epiphany of Our Lord",
      parishes: [
        "Epiphany of Our Lord Co-Cathedral Parish",
        "Immaculate Heart of Mary Parish",
        "Resurrection of the Lord",
        "St. Rose of Lima Parish"
      ]
    },
    {
      name: "Vicariate of Our Lady of Purification",
      parishes: [
        "Our Lady of Purification Parish",
        "Jesus the Nazarene Parish",
        "Divine Mercy Parish",
        "San Roque Parish",
        "San Isidro Labrador Pastoral Station"
      ]
    },
    {
      name: "Vicariate of St. Thomas Aquinas",
      parishes: [
        "Saint Thomas Aquinas Parish",
        "St. Fabian, Pope & Martyr Parish",
        "Beato Juan Martinez de Sto. Domingo Pastoral Station",
        "Virgen de la Medalla Milagrosa Parish",
        "Our Lady of the Miraculous Medal Parish",
        "Saint Hyacinth Parish"
      ]
    }
  ];

  var vicariatePageBreaks = [];

  // 4. Generate Section Breaks and Dropdowns for each Vicariate
  for (var i = 0; i < archdioceseData.length; i++) {
    var sectionPage = form.addPageBreakItem().setTitle(archdioceseData[i].name);
    vicariatePageBreaks.push(sectionPage);

    var parishDropdown = form.addListItem().setTitle('Select your Parish / Church Affiliation').setRequired(true);
    parishDropdown.setChoiceValues(archdioceseData[i].parishes);
  }

  // ---------------------------------------------------------------------
  // 5. Single-Page Roster Section for Participants 1 through 29
  // ---------------------------------------------------------------------
  var rosterSection = form.addPageBreakItem().setTitle('Delegation Roster (Participants 1–29)');

  for (var i = 0; i < vicariatePageBreaks.length; i++) {
    vicariatePageBreaks[i].setGoToPage(rosterSection);
  }

  var branchingChoices = [];
  for (var i = 0; i < archdioceseData.length; i++) {
    branchingChoices.push(vicariateQuestion.createChoice(archdioceseData[i].name, vicariatePageBreaks[i]));
  }
  vicariateQuestion.setChoices(branchingChoices);

  // Generate optional entries for Participant 1 through Participant 29 (setRequired is false)
  for (var p = 1; p <= 29; p++) {
    addParticipantFields('Participant ' + p, false);
  }

  // ---------------------------------------------------------------------
  // 6. Final Section: Payment & Verification
  // ---------------------------------------------------------------------
  form.addPageBreakItem().setTitle('Final Section: Payment and Summary Submission');

  form.addListItem().setTitle('Registration Fee Status for Delegation')
      .setChoiceValues(['Full Payment Submitted', 'Partial Payment Submitted', 'Pending Collection at Venue Entry'])
      .setRequired(true);

  form.addCheckboxItem().setTitle('Group Verification & Endorsement')
      .setChoiceValues(['By submitting this form, I certify that this roster constitutes the complete, approved delegation for our parish, endorsed by our Parish Youth Director.'])
      .setRequired(true);

  // Output logs
  Logger.log('🎉 Your Marian Youth Vigil Google Form has been generated successfully!');
  Logger.log('👉 Form Editor Link: ' + form.getEditUrl());
}