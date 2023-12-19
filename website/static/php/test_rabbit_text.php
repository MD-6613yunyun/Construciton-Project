<?php
// Include the Rabbit class
require_once('rabbit.php');


$currentDirectory = __DIR__;
$inputFileName = $currentDirectory . '/input.txt';

if (!file_exists($inputFileName)) {
    die("Input file '$inputFileName' does not exist.");
}

// Read text from the input file
$inputText = file_get_contents($inputFileName);

// Convert Unicode to Zawgyi
$zawgyiText = Rabbit::uni2zg($inputText);

$outputFileName = $currentDirectory . '/output.txt';

// Write the processed text to the output file
file_put_contents($outputFileName, $zawgyiText);

echo "Text processed and saved to '$outputFileName'.";
?>
