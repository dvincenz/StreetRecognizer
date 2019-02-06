# Project Summary

The goal of this project was to evaluate whether it was feasible to use machine learning (image recognition in particular) to automatically label the surface material of streets using ortho photos.

*See also our [presentation slides](./docs/ChallP-StreetRecognizer-Presentation.pdf) (german).*

## Challenges

### Coordinate Systems

The first issue we faced, was that the coordinate system used by swisstsopo was not the same as used by OpenStreetMaps. However, after some researching and writing a module to convert between the coordinate systems, this challenge could be solved.

### Performance

We always thought the most time-consuming process would be training our model. As it turned out, training the model was actually pretty much the best performing step of the entire project. Instead, generating the sample images to train the model and to make predictions was by far the slowest component. We had to spend a considerable amount troubleshooting and optimizing performance to arrive at an acceptable solution.

### OSM Queries

As the [Overpass API](https://overpass-turbo.eu/) already offers readily accessible OSM query interfaces, we wanted to make use of them. We quickly realized, however, that the HTTP overhead of making many thousand requests was too much. So instead we opted to download a binary extract for Switzerland and make use of [Osmosis](https://wiki.openstreetmap.org/wiki/Osmosis) to extract the data we needed. This was (way) less convenient than using the Overpass API, but orders of magnitude faster.

## Potential for improvement

### Ortho photo resolution

The ortho photos we were given for use had a resolution of 25cm per pixel. This seemed pretty decent at first glance. However, we quickly realized an average street of 2m width would only be 8 pixels wide on these photos.

Since the newest ortho photos are taken at a resolution of 10cm per pixel we could (probably) greatly increase our prediction accuracy using these photos. Simply by looking at the sample images by eye it is often impossible to distinguish between e.g. concrete and gravel.

### Try different models

All of our current models are based on [CIFAR-10](https://www.cs.toronto.edu/~kriz/cifar.html). We might achieve better results by changing the number of hidden layers or the type of the activation functions. We also had additional ideas of [completely different models](./model.md), which operate on different sizes of images or consume additional input.

### Cleaner training data

We have not done any "quality assurance" on the generated training sample images. It is very likely these images contain useless or even confusing samples, which should be removed prior to training the model.

## Conclusion

Overall the project was very interesting. It felt satisfying to work with huge data sets and achieve reasonable results. Although performance optimizations were painful, it was fun and instructive to do so in a "big data" environment.

### Input normalization is time-consuming

Most of the work had to be spent on the input normalization process. It required well over half of the project's time to simply have a functioning process to generate training sample images.

### Classes are too similar

The various surface classes we selected to classify are probably too similar. There are even cases where one class is a superset of another class, resulting in massive confusion for the model.

### Modular code structure

Our approach to split various steps of the process into separate python modules was very helpful.

### Docker development environment

Using a docker image to do all of our development work in was definitly worth it, as it streamlined the server configuration and library management process.

### Not much AI know-how gained

Keras/tensorflow abstract most of the heavy lifting, which is usually a good thing. However, in the context of learning more about machine learning, we hardly had anything to do with actualy machine learning concepts. Most of our time was spent on data conversion and normalization, to the point where we simply copied the CIFAR-10 model and achieved decent results.
