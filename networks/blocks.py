import torch
import torch.nn as nn
import torch.nn.functional as F

#### 3D U-Net building blocks
class ConvBnActivation3D(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, padding: int = None,
                 bn: bool = True,
                 activation: str = 'leakyrelu', activation_inplace: bool = True):
        super(ConvBnActivation3D, self).__init__()

        if padding is None:
            padding = (kernel_size - 1) // 2

        self.conv = nn.Conv3d(in_channels, out_channels, kernel_size=kernel_size, padding=padding, bias=False)

        if bn:
            self.bn = nn.BatchNorm3d(out_channels)
        else:
            self.bn = None

        if activation == 'relu':
            self.activation = nn.ReLU(inplace=activation_inplace)
        elif activation == 'leakyrelu' or activation == 'leaky_relu' or activation == 'lrelu':
            self.activation = nn.LeakyReLU(inplace=activation_inplace)
        elif activation == 'selu':
            self.activation = nn.SELU(inplace=activation_inplace)
        elif activation == 'elu':
            self.activation = nn.ELU(inplace=activation_inplace)
        else:
            raise NotImplementedError('Check ConvBnActivation class for available activations')

    def forward(self, x):
        x = self.conv(x)
        if self.bn:
            x = self.bn(x)
        x = self.activation(x)
        return x

class EncoderBlock3D(nn.Module):

    def __init__(self, x_channels: int, y_channels: int, kernel_size: int = 3, residual: bool = False,
                 bn: bool = True,
                 activation: str = 'leakyrelu', activation_inplace: bool = True,
                 pooling: str = 'max'):
        super(EncoderBlock3D, self).__init__()

        self.padding = (kernel_size - 1) // 2
        self.residual = residual

        self.encode = nn.Sequential(
            ConvBnActivation3D(x_channels, y_channels, kernel_size=kernel_size, padding=self.padding, bn=bn,
                               activation=activation, activation_inplace=activation_inplace),
            ConvBnActivation3D(y_channels, y_channels, kernel_size=kernel_size, padding=self.padding, bn=bn,
                               activation=activation, activation_inplace=activation_inplace),
        )
        if self.residual:
            self.encode2 = ConvBnActivation3D(y_channels + x_channels, y_channels, kernel_size=kernel_size,
                                              padding=self.padding, bn=bn, activation=activation,
                                              activation_inplace=activation_inplace)

        if pooling == 'max':
            self.pool = nn.MaxPool3d(kernel_size=2, stride=2)
        elif pooling == 'avg':
            self.pool = nn.AvgPool3d(kernel_size=2, stride=2)
        else:
            raise NotImplementedError('Check EncoderBlock3D class for available pooling operations')

    def forward(self, x: torch.Tensor):
        input_tensor = x
        x = self.encode(x)
        if self.residual:
            x = torch.cat([x, input_tensor], dim=1)
        x = self.encode2(x)
        x = self.pool(x)
        return x

class DecoderBlock3D(nn.Module):
    def __init__(self, x_external_channels: int, x_channels: int, y_channels: int, kernel_size: int = 3,
                 bn: bool = True,
                 activation: str = 'leakyrelu', activation_inplace: bool = True,
                 upsampling: str = 'trilinear'):
        super(DecoderBlock3D, self).__init__()

        padding = (kernel_size - 1) // 2
        self.deepsup = deepsup

        self.up_0 = ConvBnActivation3D(x_big_channels + x_channels, x_channels, kernel_size=kernel_size, padding=padding,
                                       bn=bn, activation=activation, activation_inplace=activation_inplace)
        self.up_1 = ConvBnActivation3D(x_channels, y_channels, kernel_size=kernel_size, padding=padding,
                                       bn=bn, activation=activation, activation_inplace=activation_inplace)
        self.upsample = nn.Upsample(scale_factor=2, mode=upsampling, align_corners=True)
        self.up_2 = ConvBnActivation3D(y_channels, y_channels, kernel_size=kernel_size, padding=padding,
                                       bn=bn, activation=activation, activation_inplace=activation_inplace)

    def forward(self, x: torch.Tensor, down_tensor: torch.Tensor):
        x = torch.cat([x, down_tensor], 1)
        x = self.up_0(x)
        skip = x
        x = self.up_1(x)
        x = self.upsample(x)
        x = self.up_2(x)

        return x, skip