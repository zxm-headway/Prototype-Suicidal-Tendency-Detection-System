import torch
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score


def evaluate(model, best_val_acc, iterator, criterion, device, logs):
    model.eval()
    epoch_loss = 0
    out_result = []
    label_result = []
    labels = []
    with torch.no_grad():
        for batch in tqdm(iterator, desc="Evaluating"):
            text, label, text_masks, post_masks = batch
            labels.append(label)
            text = text.to(device)
            label = label.to(device).float()
            text_masks = text_masks.to(device)
            post_masks = post_masks.to(device)
            output = model(text, text_masks, post_masks)
            loss = criterion(output, label)
            epoch_loss += loss.item()
            probabilities = torch.sigmoid(output)
            predicted = (probabilities > 0.5).float()
            label_result.extend(label.cpu().numpy().tolist())
            out_result.extend(predicted.cpu().numpy().tolist())
    acc = accuracy_score(label_result, out_result)
    f1_score1 = f1_score(label_result, out_result, average='binary')
    logs.info(f'Val Loss: {epoch_loss / len(iterator):.5f} | Val Acc: {acc:.5f} | Val F1: {f1_score1:.5f}')
    if acc > best_val_acc:
        best_val_acc = acc
        torch.save(model.state_dict(), './best_model.pth')
        logs.info(f'Best model saved with Val Acc: {acc:.5f}')
    return best_val_acc, acc


def test(model, iterator, device, logs):
    model.eval()
    out_result = []
    label_result = []
    with torch.no_grad():
        for batch in iterator:
            text, label, text_masks, post_masks = batch
            text = text.to(device)
            label = label.to(device).float()
            text_masks = text_masks.to(device)
            post_masks = post_masks.to(device)
            output = model(text, text_masks, post_masks)
            probabilities = torch.sigmoid(output)
            predicted = (probabilities > 0.5).float()
            label_result.extend(label.cpu().numpy().tolist())
            out_result.extend(predicted.cpu().numpy().tolist())
    acc = accuracy_score(label_result, out_result)
    f1_score1 = f1_score(label_result, out_result, average='binary')
    return acc, f1_score1


