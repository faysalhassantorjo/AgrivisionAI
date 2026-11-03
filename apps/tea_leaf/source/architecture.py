# app/ml/architecture.py

import torch
import torch.nn as nn
import timm


class AttentionFusion(nn.Module):

    def __init__(self, dim):

        super().__init__()

        self.fc = nn.Sequential(
            nn.Linear(dim * 2, dim),
            nn.ReLU(),
            nn.Linear(dim, 2)
        )

    def forward(self, d_feat, v_feat):

        # concat DenseNet + ViT features
        combined = torch.cat([d_feat, v_feat], dim=1)

        weights = torch.softmax(self.fc(combined), dim=1)

        # weighted fusion
        return (
            weights[:, 0:1] * d_feat +
            weights[:, 1:2] * v_feat
        )


class DenseNet201_FusionViT_Advanced(nn.Module):

    def __init__(self, num_classes):

        super().__init__()

        # CNN branch (DenseNet)
        self.densenet = timm.create_model(
            "densenet201",
            pretrained=False,
            features_only=True
        )

        d_chs = self.densenet.feature_info[-1]["num_chs"]

        # Transformer branch (ViT)
        self.vit = timm.create_model(
            "vit_base_patch16_224",
            pretrained=False,
            num_classes=0
        )

        self.pool = nn.AdaptiveAvgPool2d(1)

        # projection layers
        self.proj_d = nn.Linear(d_chs, 512)

        self.proj_v = nn.Linear(self.vit.num_features, 512)

        # fusion layer
        self.fusion = AttentionFusion(512)

        # classifier head
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):

        # DenseNet feature extraction
        d_feat = self.densenet(x)[-1]
        d_feat = self.pool(d_feat).view(x.size(0), -1)
        d_feat = self.proj_d(d_feat)

        # ViT feature extraction
        v_feat = self.vit(x)
        v_feat = self.proj_v(v_feat)

        # fusion
        fused = self.fusion(d_feat, v_feat)

        # classification
        return self.classifier(fused)