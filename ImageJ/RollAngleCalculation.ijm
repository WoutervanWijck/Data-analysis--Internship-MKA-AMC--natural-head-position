if (nImages == 0) { // Checkt of er wel een foto is ingeladen
    exit("Open eerst een foto!"); // anders sluit hij af met deze melding
}
imgTitle = getTitle();	// Haalt bestandsnaam van de afbeelding (slaat op in imgTitle)

run("Clear Results"); // Zorgt voor een schone measure table

setTool("line"); 
waitForUser("Stap 1", "Trek de LOODLIJN (trek de lijn over de loodlijn van boven naar beneden), klik op OK.");

//  Coördinaten van de loodlijn opslaan
getLine(vertX1, vertY1, vertX2, vertY2, vertWidth);

run("Measure");
vertAngle = getResult("Angle", nResults - 1); // Neemt de laatste meting die gedaan is

waitForUser("Stap 2", "Trek de OOGLIJN (trek de lijn tussen de exocanthia, begin bij de, voor de patient, rechter exocanthion, sleep deze vervolgens naar de, voor de patient, linker excoanthion) en klik op OK.");

// Coördinaten van de ooglijn opslaan
getLine(eyeX1, eyeY1, eyeX2, eyeY2, eyeWidth);

run("Measure");
eyeAngle = getResult("Angle", nResults - 1); // Neemt de laatste meting die gedaan is

// Berekent de roll angle ten opzichte van de loodlijn:
// Met de klok mee (CW / patiënt-rechts omlaag) is positief (+), tegen de klok in (CCW / patiënt-links omlaag) is negatief (-) => vanaf de patient gezien
rollAngle = eyeAngle - (vertAngle + 90); // vertangle +90 aangezien een perfect verticale lijn naar beneden getrokken -90 is. Een lijn van links naar rechts is 0 graden. Dus als je dat wil vergelijken moet je vertangle omzetten naar die horizontale lijn

// Zorgt dat de hoek altijd tussen -180 en 180 graden valt door er hele "rondjes" bij op te tellen
while (rollAngle > 180) rollAngle -= 360;
while (rollAngle < -180) rollAngle += 360;

// Corrigeert automatisch als de ooglijn per ongeluk van rechts naar links is getrokken (~180 graden flip)
if (rollAngle > 90) rollAngle -= 180;
if (rollAngle < -90) rollAngle += 180;

// Bepaalt de rotatierichting in tekst
if (rollAngle > 0) {
    richting = "CW (Met de klok mee / naar patient-rechts)";
} else if (rollAngle < 0) {
    richting = "CCW (Tegen de klok in / naar patient-links)";
} else {
    richting = "Neutraal";
}

// Dialoogvenster aanmaken
Dialog.create("Resultaat Roll Angle");
Dialog.addMessage("Afbeelding: " + imgTitle);
Dialog.addMessage("Verticale hoek: " + d2s(vertAngle, 2) + " graden");
Dialog.addMessage("Ooglijn hoek: " + d2s(eyeAngle, 2) + " graden");
Dialog.addMessage("Berekende Roll Angle: " + d2s(rollAngle, 2) + " graden");
Dialog.addMessage("Richting: " + richting);

// Keuzemenu's toevoegen
sessies = newArray("validatie", "session 1", "session 2");
Dialog.addChoice("Sessie:", sessies, sessies[0]);

condities = newArray("open", "closed", "mirror");
Dialog.addChoice("Conditie:", condities, condities[0]);

Dialog.addString("Opmerking / Comment:", ""); 
Dialog.show();

// Keuzes en opmerking uitlezen
sessieKeuze = Dialog.getChoice();
conditieKeuze = Dialog.getChoice();
comment = Dialog.getString();
comment = replace(comment, ",", ";"); // Komma's vervangen ter bescherming van de CSV

// Vaste opslaglocatie voor de resultaten
logPath = "Add your path";

// Header met de nieuwe kolommen Sessie en Conditie
if (!File.exists(logPath)) {
    File.append("Bestandsnaam,Sessie,Conditie,VerticaleHoek,OoglijnHoek,RollAngle,Richting,Opmerking,VertX1,VertY1,VertX2,VertY2,EyeX1,EyeY1,EyeX2,EyeY2\n", logPath);
}

// Regel samenstellen en wegschrijven
regel = imgTitle + "," + sessieKeuze + "," + conditieKeuze + "," + d2s(vertAngle, 3) + "," + d2s(eyeAngle, 3) + "," + d2s(rollAngle, 3) + "," + richting + ",\"" + comment + "\"";

// Coördinaten toevoegen aan dezelfde regel
regel = regel + "," + d2s(vertX1, 3) + "," + d2s(vertY1, 3) + "," + d2s(vertX2, 3) + "," + d2s(vertY2, 3);
regel = regel + "," + d2s(eyeX1, 3) + "," + d2s(eyeY1, 3) + "," + d2s(eyeX2, 3) + "," + d2s(eyeY2, 3) + "\n";

File.append(regel, logPath);
