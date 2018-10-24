# Model Design

## Input

We obviously require an Orthophoto as input, but we would like to give the model additional information about what we already know about the streets on that slice (e.g. location/path and street type).

### Orthophoto

Orthophoto will be sliced into equal, constant sizes / resolutions. Slices will be fed one-at-a-time to the model, as a 3 x w x h vector, represented as a flat vector.

### Street Vector Data

Street Vector Data is the Open Street Maps data, describing the street network. A street consists of a list of nodes/waypoints, describing the path the street poly-line takes.

#### Problems

* A single Orthophoto slice can contain an arbitrary number of streets
* A single street can contain an arbitrary number of nodes

#### Possible representations

* Manually render all street vector data for a given slice into an image (e.g. black-white or different colors for different street-types). Pass the rendered image as a flat vector to the model.
* Same as before, but render street vector data on a larger scale (e.g. entire Orthophoto) and slice it along with the Orthophoto.
* Instead of using vector-based street data, we could use the actually already rendered map by Open Street Maps and create matching slices on the map-images. This would save the effort of rendering the vector-data to an image and would already include different colors for street types. Probably most irrelevant information (buildings etc.) could be removed from the map, before downloading. Main problem: Might not be trivial to create exactly matching slices.

## Output

Output must, obviously, return a classification of the street's surface(s) on the given Orthophoto slice. However, there must be some reasonable way to match the outputted classes to the corresponding street, in the case that there are multiple streets with different surfaces.

### Classes

We will have a finite, discsrete and fixed number of classes, which could easily be represented in a vector.

### Street Matching

The main problem with the output, is, how we match the classes to the corresponding streets, as, again, there might be arbitrarily many streets on a given Orthophoto slice.

#### Approaches

##### Heuristic

We simply generate a single vector of classes, and then apply some heuristic to match the output back to the corresponding streets. E.g. the most probable component will be the surface of the largest street, the second most probable component the surface of the second largest street, etc. This seems extremely error-prone for slices with multiple streets of the same surface.

Of course, it should be possible to devise better performing heuristics.

##### Fixed number of streets

Instead of worrying about an unknown number of streets per slice, we could fix the number of streets on e.g. 5 on both the input and output side. This way, we would generate 5 class-vectors and easily match them to the corresponding street by enumeration. If a slice had less than 5 streets, some vectors will be left zeroed. If a slice has more than 5 streets, we either ignore the rest, or we run the same slice through the model multiple times, passing in 5 different streets each time, until we have covered all.

##### Color-coded output

Instead of having the number of classes as the size of the output-vector, we could generate a new image (same size as the Orthophoto). In this output-image, we would assign classes to every pixel, match this image back to where we know the streets are/should be, and select the highest probability of the predicted surfaces on this part of the image. The different classes and their probabilities would be encoded into the pixel-data. A trivial case would be 3 classes, where each class could correspond to a single RGB value. An advantage of this approach would be easy visualization of the output. However, this requires much more computation, as the model will generate a large amount of unnecessary predictions on pixels which aren't streets.

##### Multi-dimensional output

This approach is a variant to the `Color-coded output` approach. However, instead of caring about generating a proper image with 3 values per pixel (RGB), we would have exactly as many values per pixels, as we have classes. This would obviously result in a very large output vector and a big computational strain, but would give an exact prediction for every single pixel, which we could map back to the streets. Again, this would generate a very large amount of unnecessary predictions, which could confuse the model in training.
