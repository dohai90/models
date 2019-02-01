package com.example.dohai90.carmasking;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Environment;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.AnimationUtils;
import android.widget.ImageSwitcher;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.Toast;
import android.widget.ViewSwitcher;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    private final static int IMAGE_REQUEST_CODE = 20;
    private final static String MODEL_FILE = "frozen_inference_graph.pb";
    private final static String TAG = "Car Masking";

    private ArrayList<Bitmap> bitmaps = null;
    private Bitmap origin = null;
    private int currentImage;

    private ImageSwitcher imageSwitcher;
    private ProgressBar progressBar;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        LoadingDeepLabModel loadingModelRunner = new LoadingDeepLabModel();

        try {
            InputStream modelInputStream = getAssets().open(MODEL_FILE);
            loadingModelRunner.execute(modelInputStream);
        } catch (IOException e) {
            e.printStackTrace();
        }

        progressBar = findViewById(R.id.progressBar);
        progressBar.setVisibility(View.INVISIBLE);

        imageSwitcher = findViewById(R.id.simpleImageSwitcher);
        imageSwitcher.setFactory(new ViewSwitcher.ViewFactory() {
            @Override
            public View makeView() {
                ImageView imageView = new ImageView(getApplicationContext());
                imageView.setScaleType(ImageView.ScaleType.FIT_CENTER);
                imageView.setLayoutParams(new ImageSwitcher.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

                return imageView;
            }
        });

    }

    public void onImageSwitchingPrevClicked(View view) {
        if (bitmaps != null && bitmaps.size() != 0) {
            currentImage--;
            if (currentImage < 0) {
                currentImage = bitmaps.size() - 1;
            }
            displayCurrentBitmap();
        }
    }

    public void onImageSwitchingNextClicked(View view) {
        if (bitmaps != null && bitmaps.size() != 0) {
            currentImage++;
            if (currentImage > bitmaps.size() -1) {
                currentImage = 0;
            }
            displayCurrentBitmap();
        }
    }

    public void onImageMaskingClicked(View view) {
        MaskingImage maskingImageRunner = new MaskingImage();
        maskingImageRunner.execute(origin);

        progressBar.setVisibility(View.VISIBLE);

    }

    public void onImageSavingClicked(View view) {

    }

    /*
     * button clicked listener
     * */
    public void onImageSelectingClicked(View view) {

        Intent pickImageIntent = new Intent(Intent.ACTION_PICK);

        File imageDirectory = Environment.getExternalStoragePublicDirectory(Environment
                .DIRECTORY_PICTURES);
        String imageDirectoryPath = imageDirectory.getPath();

        Uri data = Uri.parse(imageDirectoryPath);
        pickImageIntent.setDataAndType(data, "image/*");

        startActivityForResult(pickImageIntent, IMAGE_REQUEST_CODE);
        if (bitmaps != null) {
            Log.d(TAG, "onImageSelectingClicked: bitmaps array size " + bitmaps.size());
            bitmaps.clear();
            Log.d(TAG, "onImageSelectingClicked: bitmaps array size " + bitmaps.size());
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        if (resultCode == RESULT_OK) {
            if (requestCode == IMAGE_REQUEST_CODE) {
                Uri imageUri = data.getData();
                InputStream inputStream;

                try {
                    inputStream = getContentResolver().openInputStream(imageUri);

                    origin = BitmapFactory.decodeStream(inputStream);

                    Drawable originDrawable = new BitmapDrawable(MainActivity.this.getResources(), origin);
                    imageSwitcher.setImageDrawable(originDrawable);
                    currentImage = 0;

                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                }
            }
        }
    }



    private class LoadingDeepLabModel extends AsyncTask<InputStream, Void, Boolean> {

        @Override
        protected Boolean doInBackground(InputStream... inputStreams) {
            final boolean ret = DeepLabModel.initialize(inputStreams[0]);
            return ret;
        }

        @Override
        protected void onPostExecute(Boolean result) {
            if (result == true) {
                Toast.makeText(MainActivity.this, "DeepLab Model is loaded successfully!", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private class MaskingImage extends AsyncTask<Bitmap, Void, ArrayList<Bitmap> > {
        @Override
        protected void onPostExecute(ArrayList<Bitmap> resultBitmaps) {
            bitmaps = resultBitmaps;
            progressBar.setVisibility(View.GONE);
            displayCurrentBitmap();
        }

        @Override
        protected ArrayList<Bitmap> doInBackground(Bitmap... bitmaps) {

            Bitmap origin = bitmaps[0];
            ArrayList<Bitmap> bgBitmaps = new ArrayList<>();
            bgBitmaps.add(origin);

            final int w = origin.getWidth();
            final int h = origin.getHeight();

            float resizedRatio = (float) DeepLabModel.INPUT_SIZE / Math.max(w, h);
            int resizedWidth = Math.round(resizedRatio * w);
            int resizedHeight = Math.round(resizedRatio * h);
            Log.d(TAG, "doInBackground: image is resized from : [" + w + "x" + h + "] to [" + resizedWidth + "x" + resizedHeight + "]");

            Bitmap resizedOrigin = ImageUtils.resizingBitmap(origin, resizedWidth, resizedHeight);
            Bitmap mask;
            if (DeepLabModel.isInitialized()) {
                mask = DeepLabModel.masking(resizedOrigin);
                Bitmap resizedMask = ImageUtils.resizingBitmap(mask, w, h);
                bgBitmaps.add(resizedMask);
            } else {
                mask = null;
            }

            if (mask != null) {
                Bitmap imageWithMask = ImageUtils.croppingBitmapWithMask(resizedOrigin, mask);
                Bitmap resizedImageWithMask = ImageUtils.resizingBitmap(imageWithMask, w, h);
                bgBitmaps.add(resizedImageWithMask);
            }

            return bgBitmaps;
        }
    }

    private void displayCurrentBitmap() {
        Bitmap currentBitmap = bitmaps.get(currentImage);
        Log.d(TAG, "displayCurrentBitmap: currentBitmap size: [" + currentBitmap.getWidth() + "x" + currentBitmap.getHeight() + "]");
        Drawable currentDrawable = new BitmapDrawable(MainActivity.this.getResources(), currentBitmap);
        imageSwitcher.setInAnimation(AnimationUtils.loadAnimation(MainActivity.this, android.R.anim.fade_in));
        imageSwitcher.setOutAnimation(AnimationUtils.loadAnimation(MainActivity.this, android.R.anim.fade_out));
        imageSwitcher.setImageDrawable(currentDrawable);
    }

}
