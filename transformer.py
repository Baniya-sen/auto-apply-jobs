from logging import getLogger, ERROR
from warnings import filterwarnings
from tensorflow import compat
from torch import device, cuda
from torch.utils.data import Dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import Trainer, TrainingArguments
from transformers import EarlyStoppingCallback

from config import FINE_TUNED_MODEL_PATH
from config import SUMMARY_TEXT, QUESTIONS, ANSWERS


class QADatasetCustom(Dataset):
    def __init__(self, tokenizer: T5Tokenizer, context, questions, answers, max_length=512):
        """Defined custom dataset for multiple questions with a single context"""
        self.context = context
        self.questions = questions
        self.answers = answers
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        question = self.questions[idx]
        answer = self.answers[idx]

        input_text = f"question: {question}  context: {self.context}"
        input_ids = self.tokenizer(input_text, truncation=True, padding='max_length',
                                   max_length=self.max_length, return_tensors="pt").input_ids.squeeze()
        labels = self.tokenizer(answer, truncation=True, padding='max_length',
                                max_length=self.max_length, return_tensors="pt").input_ids.squeeze()
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {"input_ids": input_ids, "labels": labels}


class QAModelCustom:
    def __init__(self, model_name='t5-small'):
        """Initializes model, tokenizer, and dataset"""
        self.model_name = model_name
        self.context = SUMMARY_TEXT
        self.questions = QUESTIONS
        self.answers = ANSWERS
        self.training_args = ()
        self.trainer = ()

        # Set TensorFlow logging level to ERROR to suppress info logs
        compat.v1.logging.set_verbosity(compat.v1.logging.ERROR)
        getLogger("transformers").setLevel(ERROR)
        filterwarnings("ignore", category=FutureWarning)

        self.device = device("cuda" if cuda.is_available() else "cpu")
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.model = self.model.to(self.device)

        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.dataset = QADatasetCustom(
            self.tokenizer, self.context, self.questions, self.answers
        )

    def train_model(self, num_train_epochs=2, patience=3) -> None:
        """Train the model based on a context, list of questions, and list of answers"""
        # Maintain epochs based on hardware(GPU or CPU)
        # You can also use Google golab to train model on faster GPU

        self.training_args = TrainingArguments(
            output_dir=FINE_TUNED_MODEL_PATH + "/results",
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
            logging_dir=FINE_TUNED_MODEL_PATH + "/logs",
            evaluation_strategy="steps",
            eval_steps=500,
            load_best_model_at_end=True,
        )

        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=self.dataset,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=patience)],
        )

        self.trainer.train()

    def save_model(self, save_path=None) -> None:
        """Save the fine-tuned pre-trained model and tokenizer to directory"""
        if not save_path:
            save_path = FINE_TUNED_MODEL_PATH

        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)


if __name__ == "__main__":
    model = QAModelCustom()
    model.train_model(num_train_epochs=35)
    model.save_model()
