# DCS-workflow metadata thoughts
Metadata schemas and whatnot to support digitization

## HONKING BIG DISCLAIMER
This is really just a pie-in-the-sky proof of concept / thought experiment
kind of thing.  Its origins are likely related to a sleepless night after 
eating junk food right before I went to bed.  Curse you, Voortman vanilla 
wafers!

## Background

We have four major areas where we digitize content:
* Digitization Services:
    * Time-based media - uses the MDPI workflow tools
    * Image-based media - uses ImageProc and varous scripts
* BDPL for born-digital content - uses manual processes and scripts
* IULMIA for film - this is a new workflow that is TBD

### General Workflow Overview

All of our digitization workflows follow the same overall structure:
* Someone requests some things to get digitized and delivers the physical media
  along with some documentation describing the metadata, etc.
* The digitization specialist will...
    * prepare the media for digitization, which may include cleaning/repair
    * digitize the media and verify it looks or sounds "right"
    * process metadata is recorded (even if it is "this one is done")
    * the files are pushed to a server somewhere
    * return the materials to the requester
* Automated systems will...
    * run some technical QC checks
    * create derivatives (as needed)
    * distribute the derivatives (as needed)
    * store the data in a preservation / archive system

### Difficulties with the current approach

Right now the processes that we use for digitization, processing, distribution,
packaging, and metadata collection vary greatly between different projects,
media types, and sometimes within the same project.  Most of this is because
we've created one-off processes that were specific to the need at hand and they
became the "go to" system for far longer than the project's lifespan.

## Goals

Ideally we should have a human- and machine-readable record of how physical
media became a digital object that can be stored with the object in a 
preservation system for future reference.

## Scope
This primarily focused on these areas:
* Describing the structure of the physical media components comprising 
  the intellectual object
    * order and description of the physical media
    * purpose of the physical media ("performance program", and the like)
* Description of the physical media
    * Physical description (type, size, length, media vendor, etc)
    * Information required for successful playback (speed, groove size, etc)
* Conservation concerns
    * Inspection details (warping, damage, fungus, etc)
    * Conservation actions (baking, freezing, cleaning, etc)
* Digitization information
    * Equipment setup details (software configuration, signal chains, etc)
    * Basic information of the produced files (duration, color space, etc)
* Processing / Packaging / Distribution Information
    * Provide hints to derivative creation (such as "audio is on stream 3")
    * Override any automated QC checks for special cases
    * defer distribution to an access/preservation system, etc.
    * Processing logs, qc checks, etc will be collected

This information is explicitly **not in scope** except to support the 
functionality above:
* Descriptive metadata
    * Only the bare minimum metadata is used to identify the physical media
    * Identifiers can be included to refer to the system of record
* Ownership / Access control
    * Only supporting communicating with the owner and returning media
    * TBD:  processing hints?
* Details about the content
    * Only information relevant to creating/playing the digital copy is 
      allowed, such as "audio volume is low on source" but not "speech begins 
      at 3 minutes"

Details of the human workflow for digitization, such as project management or
tools used, are not prescriptive -- they are intended to be illustrative of
how in-scope functionality could fit into the bigger picture or to provide an 
example of how one could include this functionality.

The first pass of this concept is targeted directly at AV and Film digitization
since there is a desire to retire the MDPI workflow tools and IULMIA will be
adding a new Film scanner in the coming months.


## File Format Syntax 
There are many human- and machine-readable file formats available.  Limiting to
formats which are:
* text-based
* commonly used
* support validation schemas

For the format examples, let's assume we want to represent the audio and 
video streams in a media file:
* there's a list of streams:  a video stream, and an audio stream.
* for a video stream we need to store the codec, resolution, pixel format, and 
  frame rate.  ('ffv1', '640x480', 'yuv_p22le', '29.97')
* for an audio stream we need to store the codec, sample rate, and number of
  channels:  ('pcm_s24le', '44100', '1')
* assume there's some schema which defines the structure, that's identified
  as `https://dlib.indiana.edu/schemas/media_streams` that's specific to 
  whatever data format the example is for.  
* the structure is illustrative -- different data structures are possible.

A few formats fit those categories:
* XML - this has been used for years for all-manners of data interchange
    * Pros: Editors available.
    * Cons: Verbose.  (Potentially) hard to read outside an editor.  Schema
      definition is a bit obnoxious and hard to write.  Verbose.
    * Example: 
    ```
    <?xml version="1.0" encoding="utf-8"?>
    <media_streams xmlns="http://dlib.indiana.edu/schemas/media_streams">
        <streams>
            <stream>
                <type>video</type>
                <codec>ffv1</codec>
                <resolution>640x480</resolution>
                <pixfmt>yuv_p22le</pixfmt>
                <framerate>29.97</framerate>
            </stream>
            <stream>
                <type>audio</type>
                <codec>pcm_s24le</codec>
                <sample_rate>44100</sample_rate>
                <channels>1</channels>
            </stream>
        </streams>
    </media_streams>
    ```
* JSON - widely used for machine-to-machine communication
    * Pros:  Syntactically simple. Can represent core datatypes.  Widely used.
      Schemas aren't hard to create.
    * Cons:  Very picky on syntax.  Easy to accidentally render unreadable.
      Schemas are implicit but can be specified in applications.  Multiline-text requires escaping newline characters.  No comments.      
    * Example:
    ```
    {
        "media_streams": [
            {
                "type": "video",
                "codec": "ffv1",
                "resolution": "640x480",
                "framerate": 29.97
            },
            {
                "type": "audio",
                "codec": "pcm_s24le",
                "sample_rate": 44100,
                "channels": 1
            }
        ]
    }
    ```
* YAML - used for configuration files, documentation examples
    * Pros: Very easy to read - the most "plain text" of the formats here.  
      Proper JSON superset.  Can use JSON Schemas for validation. Syntax is
      generally pretty forgiving. 
    * Cons: Whitespace (both count and tabs vs space) is significant.  Some
      weird corner cases with schemas when the value is number-like and a 
      string is expected.  Schemas are implicit but can be specified in 
      applications.  Comments are lost when re-rendering.
    * Example:
    ```
    media_streams:
        - type: video
          codec: ffv1
          resolution: 640x480
          framerate: 29.97
        - type: audio
          codec: pcm_s24le
          sample_rate: 44100
          channels: 1
    ```

YAML and JSON share some properties which make them especially attractive:
* They can be converted losslessly between each other.  While YAML comments
  are lost in the process, the data is intact and structured correctly.
* The data they represent are directly analogous to common data structures
  in programming languages (strings, integers, float, boolean, lists, 
  maps) so they can be loaded and used directly.
* Since YAML is a proper superset of JSON, any application expecting YAML
  data will read JSON without modification.

Since all are equally machine-usable, human-usablility is a major factor and
YAML comes out a clear winner.  See Appendix A for tools that can be used to
manually edit YAML files

The remainder of this document will use YAML.

## Schema Definition

Schemas that can be applied to YAML and JSON data can be defined using JSON
schema.  The schema is used to validate that the file conforms to what is 
expected and it can also be used by tools to provide hints for structure,
valid values, etc.








## Appendix A: Manually Editing a YAML Document

One can edit a YAML document in any text editor, but there are some caveats:
* Indentation is the structure -- so having an editor that indicates the amount
  of indentation is important, especially on deeply-nested structures.
* Tabs and spaces are not the same.  8 spaces isn't the same as a single tab.
  It is best to use an editor which doesn't insert tab (ASCII 09) characters
  into the document but instead inserts the correct number of spaces to align
  the text.  `emacs` is terrible about "optimizing" text and inserting tabs.
* If there is a schema available, using an editor which validates the document
  as it is being typed is useful.  

Everything but schema support is supplied by Visual Studio Code and when the
RedHat-supplied YAML Language Support extension is installed it gains
schema support.  Validation errors show up as the document is edited and 
CTRL+space can be used for auto completion.
