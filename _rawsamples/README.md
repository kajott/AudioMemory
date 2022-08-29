# Sample Set Directory

Put subdirectories containing WAV files here
(ideally PCM, >=32 kHz, stereo, a few seconds long).
In addition, put a single JSON file named `_info.json`
into each subdirectory with the following contents:

~~~json
{
	"name": "Display name of the sample set",
	"order": 1,
	"music": false
}
~~~

Sample sets will appear in the UI in the order
specified by the `order` value.
If there are multiple sets with the same `order`,
they will be sorted alphabetically by the directory name.

`music` specifies which icon shall be displayed
when playing back a sample: Either a musical note
(if `true`) or a speaker symbol (if `false`).


## Specifying Metadata

Additional metadata can be provided for each sample.
This will then be shown in a pop-up window that appears
when the two fields with that sample are matched.

The metadata window can contain the following information,
in that order:
- track title (`title`)
- track author or artist (`artist`)
- an image, e.g. for cover art (`image`)
- album title (`album`)
- album artist (`album_artist`)
- one line of comments (`comment`)
- a hyperlink URL (`link`)

These can be specified in any of the ways described in the sections below.

### Dedicated JSON File

Put a `.json` with the same name next to a `.wav` file.
That JSON file contains the metadata fields as a dictionary, e.g.:

~~~json
{
	"title": "Bohemian Rhapsody",
	"artist": "Queen",
	"album": "A Night at the Opera",
	"comment": "(1975)"
}
~~~

### Inside `_info.json`

Add additional keys to `_info.json` that correspond to the
name of the sample (with or without `.wav` extension), e.g.:

~~~json
{
	"name": "Beatles Greatest Hits",
	"order": 1,
	"music": true,
	"help": {
		"title": "Help!",
		"artist": "The Beatles",
		"album": "Help!",
		"comment": "(1965)"
	},
	"letitbe.wav": {
		"title": "Let It Be",
		"artist": "The Beatles",
		"album": "Let It Be",
		"comment": "(1970)"
	},
	/* [...] */
}
~~~

### Dedicated CSV File

The easiest way to edit metadata in bulk certainly is a spreadsheet application
like LibreOffice Calc or Microsoft Excel.
Using that, create a table that contains one column per metadata field
and one row per sample. In the first row, place a column heading with the
name of the column. Add a column with the fixed name `sample` to associate
each row with a sample.

A table with the example above would look like this:

| sample | title | artist | album | comment
|--------|-------|--------|-------|---------
| help | Help! | The Beatles | Help! | (1965)
| letitbe | Let It Be | The Beatles | Let It Be | (1970)
| bohemian | Bohemian Rhapsody | Queen | A Night at the Opera | (1975)

Save this table as `_metadata.csv` in the sample set directory
(i.e. along with the `.wav` files and `_info.json`) in CSV format,
and `process_samples.py` will pick it up from there.
