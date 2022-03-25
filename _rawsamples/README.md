Sample Set Directory
--------------------

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
