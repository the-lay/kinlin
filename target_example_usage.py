from kindling import *

### Very abstract overview how one would use kindling when it's done
### Ideally each file = one full experiment

# Project management
project = Project(name='my new paper', notes='doing this and that for these and those', path='C:/path')
experiment = project.new_experiment(...) # seed, experiment name,

# Dataset definition
dataset = Dataset(...)

# Network definition
class MyNewArchitecture():
    pass
network = MyNewArchitecture(...)

# Training parameters
loss = [nn.MSELoss(), nn.MSELoss()]
loss_weights = [1e4, 1]
optimizer = optim.Adam(network.parameters(), lr=0.01)

# Model definition
class MyNewModel(Model):
    # override different methods like on_epoch_start, on_training_start etc etc
    def training_fn(self, batch: torch.Tensor, batch_id: int, epoch: int) -> torch.Tensor:
        # your custom training here, this function being run for every
        pass

    def validation_fn(self, batch: torch.Tensor, batch_id: int, epoch: int):
        pass

    def on_validation_finish(self, epoch: int):
        pass

# Metrics and callbacks
metrics = []
callbacks = []

# compile model
model = MyNewModel(metrics=metrics, )

# Actual actions of the experiment
trainer = Trainer(model, dataset, optimizer, experiment=experiment)
trainer.fit(n_epochs=50, validation=True, callbacks=callbacks, verbose=True)


