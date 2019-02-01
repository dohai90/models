package com.example.dohai90.carmasking;

import android.graphics.Bitmap;
import android.graphics.Color;
import android.util.Log;

import org.tensorflow.contrib.android.TensorFlowInferenceInterface;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

public class DeepLabModel {

    private final static String TAG = "DeepLabModel";

    private final static String INPUT_NAME = "ImageTensor";
    private final static String OUTPUT_NAME = "SemanticPredictions";

    private static TensorFlowInferenceInterface sTFInferenceInterface = null;

    public final static int INPUT_SIZE = 513;

    public static ArrayList<Integer> rColor = new ArrayList<>();
    public static ArrayList<Integer> gColor = new ArrayList<>();
    public static ArrayList<Integer> bColor = new ArrayList<>();

    public static final int NUM_CLASSES = 28;

    public synchronized static boolean initialize(InputStream graphStream) {
        if (graphStream == null) {
            Log.e(TAG, "initialize: grapsh Stream failed!");
            return false;
        }

        sTFInferenceInterface = new TensorFlowInferenceInterface(graphStream);

        if (sTFInferenceInterface == null) {
            Log.e(TAG, "initialize: tensorflow inference interface failed!");
            return false;
        }

        try {
            graphStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Initializing colors
        Random rand = new Random();
        for(int i=0; i<NUM_CLASSES; i++){
            rColor.add(rand.nextInt(256));
            gColor.add(rand.nextInt(256));
            bColor.add(rand.nextInt(256));
        }

        return true;
    }

    public synchronized static boolean isInitialized() {
        return sTFInferenceInterface != null;
    }

    // getColor from class index
    public static int getColor(int classIdx){

        int a = (255 * 100 / 100) << 24 & 0xFF000000;
        int r = (rColor.get(classIdx) << 16) & 0x00FF0000;
        int g = (gColor.get(classIdx) << 8) & 0x0000FF00;
        int b = bColor.get(classIdx) & 0x000000FF;

        return a | r | g | b;
    }

    public synchronized static Bitmap masking(final Bitmap bitmap) {
        if (! isInitialized()) {
            Log.e(TAG, "masking: tensorflow inference interface is not initialized!");
            return null;
        }

        if (bitmap == null) {
            return null;
        }

        final int w = bitmap.getWidth();
        final int h = bitmap.getHeight();
        Log.d(TAG, "masking: processed bitmap size: [" + w + "x" + h + "]");

        if (w > INPUT_SIZE || h > INPUT_SIZE) {
            Log.e(TAG, "masking: invalid bitmap size" );
            return null;
        }

        int[] mIntValues = new int[w * h];
        byte[] mFlatIntValues = new byte[w * h * 3];
        int[] mLabels =  new int[w * h];

        bitmap.getPixels(mIntValues, 0, w, 0, 0, w, h);
        for (int i=0; i<mIntValues.length; i++){
            final int val = mIntValues[i];
            mFlatIntValues[i * 3 + 0] = (byte) ((val >> 16) & 0xFF);
            mFlatIntValues[i * 3 + 1] = (byte) ((val >> 8) & 0xFF);
            mFlatIntValues[i * 3 + 2] = (byte) (val & 0xFF);
        }

        final long start = System.currentTimeMillis();
        sTFInferenceInterface.feed(INPUT_NAME, mFlatIntValues, 1, h, w, 3);
        sTFInferenceInterface.run(new String[] {OUTPUT_NAME}, true);
        sTFInferenceInterface.fetch(OUTPUT_NAME, mLabels);
        final long end = System.currentTimeMillis();

        Log.d(TAG, "masking: inference takes: " + (end - start) + " milisecs");
        Log.d(TAG, "masking: labels: " + Arrays.toString(mLabels));

        Bitmap output = Bitmap.createBitmap(w, h ,Bitmap.Config.ARGB_8888);
        for (int y=0; y<h; y++) {
            for (int x=0; x<w; x++) {
                output.setPixel(x, y, mLabels[y * w + x] == 0 ? Color.TRANSPARENT : getColor(mLabels[y * w + x]));
            }
        }
        return output;
    }
}
